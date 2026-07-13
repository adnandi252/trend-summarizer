import os
import re
import json
import logging
import nltk
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logger.info("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    logger.info("Downloading NLTK punkt_tab...")
    nltk.download('punkt_tab', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    logger.info("Downloading NLTK stopwords...")
    nltk.download('stopwords', quiet=True)

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords as nltk_stopwords

# Initialize Sastrawi Stemmer
logger.info("Initializing Sastrawi Stemmer...")
stemmer_factory = StemmerFactory()
sastrawi_stemmer = stemmer_factory.create_stemmer()

# Caching for Sastrawi Stemmer to speed up processing
CACHE_PATH = "data/stem_cache.json"
STEM_CACHE = {}

def load_stem_cache():
    global STEM_CACHE
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                STEM_CACHE = json.load(f)
            logger.info(f"Loaded {len(STEM_CACHE)} stemmed words from cache file.")
        except Exception as e:
            logger.warning(f"Failed to load stem cache: {e}")

def save_stem_cache():
    if STEM_CACHE:
        try:
            os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
            with open(CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(STEM_CACHE, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved {len(STEM_CACHE)} stemmed words to cache file.")
        except Exception as e:
            logger.warning(f"Failed to save stem cache: {e}")

def stem_word(word: str) -> str:
    """
    Stems a single word using Sastrawi with a global cache.
    """
    if word in STEM_CACHE:
        return STEM_CACHE[word]
    stemmed = sastrawi_stemmer.stem(word)
    STEM_CACHE[word] = stemmed
    return stemmed

# Build unified stopwords set
try:
    indonesian_stop = set(nltk_stopwords.words('indonesian'))
except Exception:
    logger.warning("Failed to load NLTK indonesian stopwords, using empty fallback.")
    indonesian_stop = set()
try:
    english_stop = set(nltk_stopwords.words('english'))
except Exception:
    logger.warning("Failed to load NLTK english stopwords, using empty fallback.")
    english_stop = set()

custom_stops = {
    "yang", "di", "dan", "ke", "dari", "untuk", "dengan", "ini", "itu", "atau", 
    "adalah", "pada", "juga", "saya", "kami", "mereka", "dia", "anda", "telah",
    "dalam", "oleh", "serta", "karena", "tersebut", "bisa", "ada", "lebih",
    "bagi", "akan", "dapat", "ia", "sebagai", "bahwa", "tidak", "hanya", "seperti",
    "yaitu", "para", "namun", "terkait", "mengatakan", "menjadi", "juga",
    "tentang", "hanya", "dari", "ia", "oleh", "hingga", "dalam", "setelah", "namun",
    "sebuah", "salah", "satu", "ia", "telah", "ia", "serta", "atau", "ada", "bisa",
    "olehnya", "selain", "ia", "bahwasanya", "jika", "maka", "apabila", "saat",
    "saatnya", "begitu", "sehingga", "serta", "berbagai", "secara", "terhadap",
    "melalui", "maupun", "lalu", "kemudian", "kepada", "kembali", "banyak", "beberapa",
    "hal", "tersebut", "ia", "kita", "kamu", "dia", "mereka", "anda", "kalian", "mereka"
}

ALL_STOPWORDS = indonesian_stop.union(english_stop).union(custom_stops)

def clean_text_full(text: str) -> str:
    """
    Cleans raw text by removing HTML tags, URLs, email addresses, digits, special characters, and emojis.
    Returns cleaned lowercase text.
    """
    if not text:
        return ""
    
    # 1. Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # 2. Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # 3. Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # 4. Remove digits and numbers
    text = re.sub(r'\d+', '', text)
    
    # 5. Remove special characters/punctuation/emojis (keep letters and spaces)
    text = re.sub(r'[^a-zA-Z\s\-]', ' ', text)
    
    # 6. Normalize multiple spaces/newlines to a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 7. Convert to lowercase
    return text.lower()

def preprocess_article(text: str) -> tuple:
    """
    Preprocesses raw article text: cleans, tokenizes, removes stopwords, and stems words.
    Returns a tuple of (clean_text, clean_tokens).
    """
    # Step 1: Clean text
    cleaned_text = clean_text_full(text)
    
    # Step 2: Tokenize
    tokens = word_tokenize(cleaned_text)
    
    # Step 3 & 4: Stopword removal and Stemming
    clean_tokens = []
    for token in tokens:
        # Resolve hyphenated words (e.g., 'toko-toko' -> stem both or keep)
        # We can split hyphenated words to handle them better in Indonesian
        sub_tokens = token.split('-')
        for st in sub_tokens:
            st = st.strip()
            if st and st not in ALL_STOPWORDS and len(st) > 2:
                stemmed = stem_word(st)
                if stemmed and stemmed not in ALL_STOPWORDS and len(stemmed) > 2:
                    clean_tokens.append(stemmed)
                    
    # Reconstruct clean_text from clean_tokens
    reconstructed_text = " ".join(clean_tokens)
    
    return reconstructed_text, clean_tokens

def run_preprocessing_pipeline(input_path: str = "data/raw_articles.json", output_path: str = "data/preprocessed_articles.json") -> str:
    """
    Loads raw articles, preprocesses each, and saves the cleaned dataset.
    """
    # Load stem cache from disk if it exists
    load_stem_cache()
    
    logger.info(f"Loading raw dataset from: {input_path}")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} does not exist.")
        
    with open(input_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
        
    logger.info(f"Preprocessing {len(articles)} articles...")
    preprocessed_articles = []
    
    # Track progress and cache performance
    total = len(articles)
    for idx, art in enumerate(articles, 1):
        raw_text = art.get("raw_text", "")
        clean_text, clean_tokens = preprocess_article(raw_text)
        
        # Create a new dictionary to preserve original fields and append preprocessed fields
        new_art = art.copy()
        new_art["clean_text"] = clean_text
        new_art["clean_tokens"] = clean_tokens
        preprocessed_articles.append(new_art)
        
        if idx % 20 == 0 or idx == total:
            logger.info(f"Processed {idx}/{total} articles. Stem cache size: {len(STEM_CACHE)}")
            
    # Save back to JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(preprocessed_articles, f, indent=4, ensure_ascii=False)
        logger.info(f"Preprocessing complete. Cleaned dataset saved to: {output_path}")
    except Exception as e:
        logger.error(f"Failed to save preprocessed dataset: {e}")
        raise e
        
    # Save cache back to disk
    save_stem_cache()
    
    return output_path

if __name__ == "__main__":
    # Test on dummy text
    sample_text = (
        "Industri FMCG di Indonesia tengah menerapkan teknologi digital untuk meningkatkan efisiensi. "
        "Peritel modern versus koperasi tradisional saling bersaing memperebutkan hati para konsumen."
    )
    print("Testing preprocess_article on sample text:")
    clean_txt, tokens = preprocess_article(sample_text)
    print("Cleaned text:", clean_txt)
    print("Tokens:", tokens)
    
    # Run pipeline on test data if exists
    test_input = "data/raw_articles.json"
    test_output = "data/preprocessed_articles.json"
    if os.path.exists(test_input):
        print("\nRunning pipeline on raw_articles.json...")
        run_preprocessing_pipeline(test_input, test_output)
