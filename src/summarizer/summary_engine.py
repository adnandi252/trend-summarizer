import os
import json
import logging
import nltk
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure NLTK punkt tokenizer is present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

# Try importing transformers and torch
try:
    import torch
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Hugging Face transformers or torch not installed. Generative summaries will use narrative fallback.")

class SummaryEngine:
    def __init__(self, model_name="cahya/t5-base-indonesian-summarization-cased"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.model_loaded = False

    def load_generative_model(self):
        """
        Loads the Hugging Face summarization model if available.
        """
        if not TRANSFORMERS_AVAILABLE:
            return False
        if self.model_loaded:
            return True
            
        logger.info(f"Attempting to load generative model: {self.model_name}...")
        try:
            # Set socket/download timeout implicitly and configure CPU usage limits if needed
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=False)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name, local_files_only=False)
            
            # Use GPU if available
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
            self.model_loaded = True
            logger.info(f"Generative model loaded successfully on device: {self.device}.")
            return True
        except Exception as e:
            logger.error(f"Failed to load Hugging Face model {self.model_name}: {e}. Falling back to narrative synthesis.")
            self.model_loaded = False
            return False

    def extractive_summary(self, text: str, num_sentences: int = 3) -> str:
        """
        Generates an extractive summary using the TextRank (PageRank) algorithm on TF-IDF sentence vectors.
        """
        if not text or not text.strip():
            return ""
            
        # Tokenize text into sentences
        try:
            sentences = nltk.sent_tokenize(text)
        except Exception:
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
        # Strip and clean sentence list
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) <= num_sentences:
            return " ".join(sentences)
            
        # Compute sentence similarities using TF-IDF and Cosine Similarity
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=1)
        try:
            tfidf_matrix = vectorizer.fit_transform(sentences)
        except ValueError:
            # Empty vocabulary or tokenization issue, return first few sentences
            return " ".join(sentences[:num_sentences])
            
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Build NetworkX similarity graph
        nx_graph = nx.from_numpy_array(similarity_matrix)
        
        # Compute PageRank scores
        try:
            scores = nx.pagerank(nx_graph, max_iter=200)
        except Exception as e:
            logger.warning(f"PageRank convergence failed: {e}. Fallback to sentence order.")
            return " ".join(sentences[:num_sentences])
            
        # Rank sentences and select the top ones
        ranked_sentences = sorted(((scores[i], s, i) for i, s in enumerate(sentences)), reverse=True)
        top_sentence_indices = {item[2] for item in ranked_sentences[:num_sentences]}
        
        # Re-sort to maintain original document flow/chronology
        final_sentences = [sentences[i] for i in sorted(top_sentence_indices)]
        return " ".join(final_sentences)

    def generative_summary(self, text: str) -> str:
        """
        Generates a generative brief summary using the HF Seq2Seq pipeline.
        Returns None if model fails to load or run.
        """
        if not text or not text.strip():
            return ""
            
        if self.load_generative_model():
            logger.info("Generating generative summary using T5 model...")
            try:
                # Direct PyTorch generation bypassing pipeline validation limits
                inputs = self.tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
                # Move inputs to same device as model
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Generate summary token IDs
                summary_ids = self.model.generate(
                    inputs["input_ids"],
                    max_length=150,
                    min_length=40,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )
                # Decode to string
                summary_text = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                if summary_text:
                    return summary_text.strip()
            except Exception as e:
                logger.error(f"Error during generative summarization: {e}. Using fallback.")
        return None

    def generative_summary_groq(self, text: str, category_name: str = "Umum", api_key: str = None, model_name: str = "llama-3.1-8b-instant") -> str:
        """
        Generates a generative brief summary using the Groq API Cloud platform.
        """
        api_key = api_key or os.getenv("API_KEY") or os.getenv("GROQ_API_KEY")
        api_base = os.getenv("API_BASE_URL") or os.getenv("GROQ_API_BASE") or "https://api.groq.com/openai/v1"
        if not api_key:
            logger.warning("API key not provided or found in environment. Skipping summarization.")
            return None
            
        import requests
        logger.info(f"Generating generative summary using model: {model_name} at base: {api_base}...")
        url = f"{api_base.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = (
            "Anda adalah seorang Analis Riset Pasar dan Strategi Bisnis senior. "
            "Tugas Anda adalah menulis laporan Executive Summary (Ringkasan Eksekutif) yang komprehensif, mendalam, "
            f"dan profesional dalam Bahasa Indonesia mengenai tren industri '{category_name}' berdasarkan berita-berita pendukung berikut.\n\n"
            "Laporan Anda harus terstruktur dengan format paragraf mengalir bebas (3 paragraf terpisah tanpa sub-heading atau bullet points) "
            "dan mencakup tiga aspek utama berikut:\n"
            "1. Latar Belakang & Status Saat Ini: Jelaskan apa tren utamanya dan isu krusial yang sedang diangkat.\n"
            "2. Dampak & Implikasi Lapangan: Uraikan fakta konkret, keterlibatan pihak terkait, serta dampak langsung ke pasar.\n"
            "3. Prospek & Outlook Masa Depan: Jelaskan bagaimana tren ini diperkirakan akan berkembang dan memengaruhi industri ke depan.\n\n"
            f"BERITA PENDUKUNG:\n{text}\n\n"
            "Tulis langsung ringkasan eksekutif komprehensif (minimal 3 paragraf) tersebut sekarang:"
        )
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 2048
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            if response.status_code == 200:
                text_content = response.content.decode('utf-8').strip()
                start_idx = text_content.find("{")
                end_idx = text_content.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    text_content = text_content[start_idx:end_idx+1]
                import json
                data = json.loads(text_content, strict=False)
                summary = data["choices"][0]["message"]["content"]
                return summary.strip()
            else:
                logger.error(f"Groq API returned error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to communicate with Groq API: {e}")
        return None

    def generate_insights_groq(self, text: str, category_name: str = "Umum", api_key: str = None, model_name: str = "llama-3.1-8b-instant") -> dict:
        """
        Generates a generative summary, emerging market opportunities, and consumer behavior shifts
        using the Groq API Cloud platform, returned as a structured dictionary.
        """
        api_key = api_key or os.getenv("API_KEY") or os.getenv("GROQ_API_KEY")
        api_base = os.getenv("API_BASE_URL") or os.getenv("GROQ_API_BASE") or "https://api.groq.com/openai/v1"
        if not api_key:
            logger.warning("API key not provided or found in environment. Skipping summarization.")
            return None
            
        import requests
        logger.info(f"Generating generative summary and insights using model: {model_name} at base: {api_base}...")
        url = f"{api_base.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = (
            "Anda adalah seorang Analis Data senior yang bertugas menyusun ringkasan informasi pasar secara objektif, detail, padat, dan faktual.\n"
            "Tugas Anda adalah menulis ringkasan eksekutif dan temuan dalam Bahasa Indonesia mengenai tren industri "
            f"'{category_name}' berdasarkan berita-berita pendukung berikut.\n\n"
            "Anda WAJIB memberikan respon HANYA dalam format JSON yang valid dengan struktur berikut:\n"
            "{\n"
            '  "generative_brief": "Tuliskan ringkasan eksekutif yang sangat jelas, detail, padat, dan terstruktur secara harfiah dengan format 4 poin berikut (pisahkan antar poin dengan karakter newline \\n):\n\n'
            '**Executive Brief**\n'
            '1. Tren Utama: [Analisis mendalam mengenai tren utama industri yang sedang berkembang, didukung data konkret dari berita]\n'
            '2. Ringkasan: [Ringkasan yang padat, lengkap, dan kaya informasi faktual mencakup nama-nama perusahaan, angka investasi, regulasi, dan detail operasional dari berita]\n'
            '3. Sentimen Pasar: [Analisis sentimen pasar/konsumen secara tajam, objektif, dan bernilai strategis berdasarkan fakta berita]\n'
            '4. Rekomendasi: [Rekomendasi taktis, aplikatif, dan strategis bagi bisnis untuk menyikapi tren ini secara proaktif]",\n'
            '  "market_opportunities": [\n'
            '    {"title": "Nama Peluang Pasar 1", "desc": "Penjelasan singkat dan objektif mengenai peluang pasar berdasarkan berita"},\n'
            '    {"title": "Nama Peluang Pasar 2", "desc": "Penjelasan singkat dan objektif mengenai peluang pasar berdasarkan berita"}\n'
            '  ],\n'
            '  "consumer_behavior": [\n'
            '    {"title": "Nama Pergeseran Perilaku 1", "desc": "Penjelasan singkat dan objektif mengenai pergeseran perilaku konsumen berdasarkan berita"},\n'
            '    {"title": "Nama Pergeseran Perilaku 2", "desc": "Penjelasan singkat dan objektif mengenai pergeseran perilaku konsumen berdasarkan berita"}\n'
            '  ]\n'
            "}\n\n"
            f"BERITA PENDUKUNG:\n{text}\n\n"
            "Pastikan JSON valid, tidak terpotong, dan gunakan bahasa Indonesia yang formal, lugas, dan objektif. "
            "PENTING: Jangan melebih-lebihkan narasi (hindari hiperbola atau klaim bombastis yang tidak ada di berita). "
            "PENTING: Gunakan tanda kutip tunggal (') untuk tanda kutip di dalam nilai teks (misalnya 'Indonesia Emas', jangan gunakan tanda kutip ganda internal) agar format JSON tidak rusak. "
            "PENTING: Jangan menulis teks pengantar, penjelasan, markdown, atau pembuka/penutup apapun di luar JSON. Respon Anda harus HANYA berupa JSON valid yang langsung diawali dengan '{' dan diakhiri dengan '}'."
        )
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 2048
        }
        
        if any(x in model_name.lower() for x in ["llama", "qwen", "gemma", "test-1"]):
            payload["response_format"] = {"type": "json_object"}
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                text_content = response.content.decode('utf-8').strip()
                start_idx = text_content.find("{")
                end_idx = text_content.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    text_content = text_content[start_idx:end_idx+1]
                import json
                data = json.loads(text_content, strict=False)
                raw_response = data["choices"][0]["message"]["content"].strip()
                
                # Robust extraction
                start_idx = raw_response.find("{")
                end_idx = raw_response.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    json_str = raw_response[start_idx:end_idx+1]
                else:
                    json_str = raw_response
                
                parsed_data = json.loads(json_str, strict=False)
                return {
                    "generative_brief": parsed_data.get("generative_brief", ""),
                    "market_opportunities": parsed_data.get("market_opportunities", []),
                    "consumer_behavior": parsed_data.get("consumer_behavior", [])
                }
            else:
                logger.error(f"Groq API returned error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to communicate with Groq API or parse JSON: {e}")
        return None


def run_summarization_pipeline(
    input_path: str = "data/clustered_articles.json",
    output_path: str = "data/final_summary_report.json",
    model_source: str = "local",
    groq_api_key: str = None,
    groq_model: str = None
) -> str:
    """
    Groups clustered articles by category, runs hierarchical summarization,
    and writes the final executive brief report.
    """
    logger.info(f"Loading clustered articles from: {input_path}")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} does not exist.")
        
    with open(input_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
        
    # Group articles by category
    categories = {}
    for art in articles:
        cat = art.get("trend_category", "Uncategorized")
        if cat not in categories:
            categories[cat] = []
            categories[cat].append(art)
        else:
            categories[cat].append(art)
            
    engine = SummaryEngine()
    final_report = {}
    
    for cat_name, cat_articles in categories.items():
        logger.info(f"Processing category '{cat_name}' containing {len(cat_articles)} articles...")
        
        # Hierarchical TextRank to avoid huge matrix sizes
        # Extract top 2 sentences from each article first
        rep_sentences = []
        for art in cat_articles:
            raw_text = art.get("raw_text", "")
            if len(raw_text.strip()) > 50:
                top_2 = engine.extractive_summary(raw_text, num_sentences=2)
                if top_2:
                    rep_sentences.append(top_2)
                    
        combined_reps = " ".join(rep_sentences)
        
        # Get final top 5 representative sentences
        extractive_brief = engine.extractive_summary(combined_reps, num_sentences=5)
        
        # Retrieve cluster keywords (shared in articles)
        keywords = cat_articles[0].get("cluster_keywords", [])
        
        # Generate narrative brief and insights
        generative_brief = None
        market_opportunities = []
        consumer_behavior = []
        
        if model_source == "groq":
            resolved_key = groq_api_key or os.getenv("API_KEY") or os.getenv("GROQ_API_KEY")
            if not resolved_key:
                raise ValueError("API Key (9router/Groq) tidak dikonfigurasi di server backend (.env atau parameter kosong).")
            default_model = "test-1" if "9router" in (os.getenv("API_BASE_URL") or os.getenv("GROQ_API_BASE") or "") else "llama-3.1-8b-instant"
            model = groq_model or default_model
            
            try:
                groq_data = engine.generate_insights_groq(
                    extractive_brief, 
                    category_name=cat_name, 
                    api_key=resolved_key, 
                    model_name=model
                )
                if groq_data and groq_data.get("generative_brief"):
                    generative_brief = groq_data["generative_brief"]
                    market_opportunities = groq_data.get("market_opportunities", [])
                    consumer_behavior = groq_data.get("consumer_behavior", [])
                    logger.info("Generative summary and insights generated using Groq API successfully.")
                else:
                    raise RuntimeError("API tidak mengembalikan data ringkasan generatif.")
            except Exception as ex:
                logger.error(f"Error calling Groq API: {ex}")
                raise RuntimeError(f"Gagal melakukan ringkasan generatif via API: {ex}")
        elif model_source == "local":
            logger.info("Menggunakan model lokal T5 untuk ringkasan generatif...")
            t5_summary = engine.generative_summary(extractive_brief)
            if t5_summary:
                generative_brief = t5_summary
                market_opportunities = []
                consumer_behavior = []
            else:
                raise RuntimeError("Gagal memuat atau menjalankan model T5 lokal.")
        else:
            raise ValueError(f"Sumber model tidak dikenal: {model_source}")
            
        if not generative_brief:
            raise RuntimeError("Gagal menghasilkan ringkasan generatif.")
            
        # Collect article details for metadata report
        supporting_articles = []
        for art in cat_articles:
            supporting_articles.append({
                "id": art.get("id"),
                "title": art.get("title"),
                "url": art.get("url"),
                "source": art.get("source"),
                "publish_date": art.get("publish_date")
            })
            
        final_report[cat_name] = {
            "trend_category": cat_name,
            "article_count": len(cat_articles),
            "top_keywords": keywords,
            "extractive_brief": extractive_brief,
            "generative_brief": generative_brief,
            "market_opportunities": market_opportunities,
            "consumer_behavior": consumer_behavior,
            "articles": supporting_articles
        }
        
    # Save the final report
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=4, ensure_ascii=False)
        logger.info(f"Final summary report successfully saved to: {output_path}")
    except Exception as e:
        logger.error(f"Failed to save final summary report: {e}")
        raise e
        
    return output_path

if __name__ == "__main__":
    test_input = "data/clustered_articles.json"
    test_output = "data/final_summary_report.json"
    if os.path.exists(test_input):
        print("\nRunning summarization pipeline on clustered_articles.json...")
        run_summarization_pipeline(test_input, test_output)
    else:
        # Dummy dry-run
        print("Dataset not found. Testing extractive TextRank on dummy text:")
        dummy_text = (
            "Kopi luwak adalah produk unggulan koperasi desa. "
            "Pemerintah mendorong koperasi lokal agar bersaing di pasar retail modern merah putih. "
            "Para petani kopi di pedesaan terbantu oleh regulasi perlindungan komoditas ini. "
            "Peningkatan jaringan logistik pedesaan memicu efisiensi distribusi barang pokok. "
            "Hampir seluruh minimarket di kota besar kini menerima pasokan langsung dari perkebunan rakyat."
        )
        engine = SummaryEngine()
        ext = engine.extractive_summary(dummy_text, num_sentences=2)
        print("TextRank Summary:\n", ext)
        narr = engine.generate_fallback_narrative("Sustainability", 12, ["koperasi", "ritel", "desa"], ext)
        print("Narrative Summary:\n", narr)
