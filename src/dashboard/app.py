import os
import json
import pandas as pd
import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="AI Trend Summarization & Monitoring Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using HTML/CSS
st.markdown("""
    <style>
    /* Main body background and fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Title gradient */
    .title-gradient {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF8533 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    /* Card design */
    .premium-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        margin-bottom: 1rem;
    }
    
    /* Styled tag badges for keywords */
    .keyword-badge {
        display: inline-block;
        background: linear-gradient(135deg, #3385ff 0%, #0052cc 100%);
        color: white;
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    }
    
    /* Subsection headings */
    .section-header {
        font-size: 1.5rem;
        color: #ff9955;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)

# Path definition
SUMMARY_PATH = "data/final_summary_report.json"
FEEDBACK_PATH = "data/user_feedback.json"
EVAL_PATH = "data/evaluation_results.json"

def load_json_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")
    return None

# Load dataset
report = load_json_data(SUMMARY_PATH)
eval_results = load_json_data(EVAL_PATH)

# Title & Description
st.markdown('<p class="title-gradient">Trend Summarization & Insights Dashboard</p>', unsafe_allow_html=True)
st.markdown("##### *Monitoring & Peringkasan AI Tren Industri Retail, E-Commerce, dan FMCG Indonesia* 🇮🇩")
st.markdown("---")

if not report:
    st.warning("⚠️ Laporan ringkasan akhir (`data/final_summary_report.json`) belum tersedia. Harap jalankan pipeline terlebih dahulu.")
else:
    # Sidebar
    st.sidebar.image("https://img.icons8.com/nolan/96/combo-chart.png", width=80)
    st.sidebar.markdown("### Navigasi Dashboard")
    page = st.sidebar.radio("Pilih Halaman:", ["Analisis Tren & Ringkasan", "Evaluasi Model (ROUGE)", "Umpan Balik Pengguna"])

    # Extract all articles for global count and metrics
    all_articles = []
    category_metrics = {}
    for cat_name, cat_data in report.items():
        count = cat_data.get("article_count", 0)
        category_metrics[cat_name] = count
        for art in cat_data.get("articles", []):
            art["trend_category"] = cat_name
            all_articles.append(art)
            
    df_articles = pd.DataFrame(all_articles)

    if page == "Analisis Tren & Ringkasan":
        # Section 1: KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Artikel Terkumpul", len(df_articles))
        with col2:
            st.metric("Tren Digital Marketing", category_metrics.get("Digital Marketing", 0))
        with col3:
            st.metric("Tren Sustainability", category_metrics.get("Sustainability", 0))
        with col4:
            st.metric("Tren Consumer Behavior", category_metrics.get("Consumer Behavior Shift", 0))

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Section 2: Distribution Chart & Keywords
        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown('<p class="section-header">Distribusi Topik Tren</p>', unsafe_allow_html=True)
            # Create a simple horizontal bar chart
            chart_data = pd.DataFrame({
                'Kategori': list(category_metrics.keys()),
                'Jumlah Artikel': list(category_metrics.values())
            })
            st.bar_chart(data=chart_data, x='Kategori', y='Jumlah Artikel', color='#FF4B4B')

        with col_right:
            st.markdown('<p class="section-header">Kata Kunci Tren Dominan</p>', unsafe_allow_html=True)
            # Display keyword pills per category
            for cat_name, cat_data in report.items():
                st.write(f"**{cat_name}:**")
                keywords_html = "".join([f'<span class="keyword-badge">{kw}</span>' for kw in cat_data.get("top_keywords", [])])
                st.markdown(keywords_html, unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:0.8rem;'></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Section 3: Dynamic Summarization Panel
        st.markdown('<p class="section-header">Executive Summary Briefs</p>', unsafe_allow_html=True)
        selected_cat = st.selectbox("Pilih Kategori Tren Untuk Menampilkan Ringkasan:", list(report.keys()))
        
        if selected_cat:
            cat_data = report[selected_cat]
            col_ext, col_gen = st.columns([1, 1])
            
            with col_ext:
                st.subheader("📌 Extractive Summary (Poin Kunci)")
                st.info("Algoritma TextRank (PageRank) memilih kalimat-kalimat paling representatif dari kluster artikel.")
                # Render bullet points nicely
                sentences = [s.strip() for s in cat_data.get("extractive_brief", "").split('.') if s.strip()]
                for s in sentences:
                    st.markdown(f"- {s}.")
                    
            with col_gen:
                st.subheader("✍️ Generative Summary (Naratif Eksekutif)")
                st.success("Ringkasan naratif eksekutif terstruktur yang disintesis secara cerdas.")
                st.markdown(f"<div class='premium-card' style='font-size:1.05rem; line-height:1.6;'>{cat_data.get('generative_brief', '')}</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Section 4: Articles Table
        st.markdown('<p class="section-header">Industry Insight Monitoring Table</p>', unsafe_allow_html=True)
        st.write("Cari dan filter artikel pendukung hasil scraping:")
        
        search_query = st.text_input("🔍 Cari berdasarkan judul atau sumber:")
        filter_cat = st.multiselect("Filter Kategori:", list(report.keys()), default=list(report.keys()))
        
        # Filter dataframe
        filtered_df = df_articles.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df['title'].str.contains(search_query, case=False, na=False) |
                filtered_df['source'].str.contains(search_query, case=False, na=False)
            ]
        if filter_cat:
            filtered_df = filtered_df[filtered_df['trend_category'].isin(filter_cat)]
            
        # Format table representation
        if not filtered_df.empty:
            # Reorder and rename columns
            display_df = filtered_df[['id', 'title', 'source', 'publish_date', 'trend_category', 'url']]
            display_df.columns = ['ID', 'Judul Artikel', 'Sumber', 'Tanggal Terbit', 'Kategori Tren', 'Link URL']
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.write("Tidak ada artikel yang cocok dengan filter pencarian.")

    elif page == "Evaluasi Model (ROUGE)":
        st.markdown('<p class="title-gradient" style="font-size: 2.2rem;">Evaluasi Kualitas Ringkasan AI</p>', unsafe_allow_html=True)
        st.write(
            "Mengukur performa ringkasan otomatis (Extractive & Generative) terhadap ringkasan acuan manusia "
            "(*ground truth summaries*) menggunakan metrik ROUGE (Recall-Oriented Understudy for Gisting Evaluation)."
        )
        st.markdown("---")

        if not eval_results:
            st.warning("⚠️ Berkas evaluasi (`data/evaluation_results.json`) belum tersedia. Harap jalankan script evaluasi.")
        else:
            col_left, col_right = st.columns([1.2, 1])
            with col_left:
                st.markdown('<p class="section-header">Tabel Hasil ROUGE Score</p>', unsafe_allow_html=True)
                
                # Transform eval results to dataframe for visualization
                eval_rows = []
                for category, types in eval_results.items():
                    for type_name, metrics in types.items():
                        for rouge_metric, scores in metrics.items():
                            eval_rows.append({
                                "Kategori": category,
                                "Tipe Ringkasan": type_name.capitalize(),
                                "Metrik": rouge_metric.upper(),
                                "Precision": round(scores["precision"], 4),
                                "Recall": round(scores["recall"], 4),
                                "F1-Score": round(scores["fmeasure"], 4)
                            })
                df_eval = pd.DataFrame(eval_rows)
                st.dataframe(df_eval, use_container_width=True, hide_index=True)
                
            with col_right:
                st.markdown('<p class="section-header">Interpretasi Metrik</p>', unsafe_allow_html=True)
                st.markdown("""
                *   **ROUGE-1**: Mengukur kecocokan kata tunggal (*unigram*). Menunjukkan tingkat pemeliharaan konten informasi penting.
                *   **ROUGE-2**: Mengukur kecocokan pasangan kata berurutan (*bigram*). Menunjukkan tingkat kelancaran dan kesinambungan struktur kalimat.
                *   **ROUGE-L**: Mengukur Subsekuen Terpanjang Bersama (*Longest Common Subsequence*). Menunjukkan kesamaan struktur tata bahasa dan susunan kalimat.
                *   **F1-Score**: Rata-rata harmonis antara *Precision* (seberapa banyak kata hasil AI yang relevan) dan *Recall* (seberapa banyak kata acuan manusia yang tertangkap oleh AI).
                """)
                
                # Plot average F1-scores
                st.markdown("**Rata-rata F1-Score per Tipe Ringkasan:**")
                avg_f1 = df_eval.groupby("Tipe Ringkasan")["F1-Score"].mean().reset_index()
                st.bar_chart(avg_f1, x="Tipe Ringkasan", y="F1-Score", color="#FF8533")

    elif page == "Umpan Balik Pengguna":
        st.markdown('<p class="title-gradient" style="font-size: 2.2rem;">Human Review Log</p>', unsafe_allow_html=True)
        st.write("Berikan rating dan feedback Anda terhadap hasil ringkasan AI untuk membantu menyempurnakan performa model.")
        st.markdown("---")

        # Load existing feedback list
        feedback_list = []
        if os.path.exists(FEEDBACK_PATH):
            try:
                with open(FEEDBACK_PATH, 'r', encoding='utf-8') as f:
                    feedback_list = json.load(f)
            except Exception:
                feedback_list = []

        # Feedback entry form
        st.subheader("Kirim Review Baru")
        with st.form("feedback_form", clear_on_submit=True):
            category_selection = st.selectbox("Pilih Kategori Tren yang Dinilai:", list(report.keys()))
            rating = st.radio("Rating Kualitas Ringkasan:", ["Sangat Baik 👍", "Cukup Baik 👌", "Perlu Perbaikan 👎"])
            comments = st.text_area("Masukkan komentar/masukan spesifik Anda:")
            submitted = st.form_submit_submit_button("Simpan Umpan Balik")
            
            if submitted:
                new_feedback = {
                    "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "kategori_tren": category_selection,
                    "rating": rating,
                    "komentar": comments
                }
                feedback_list.append(new_feedback)
                try:
                    with open(FEEDBACK_PATH, 'w', encoding='utf-8') as f:
                        json.dump(feedback_list, f, indent=4, ensure_ascii=False)
                    st.success("Umpan balik berhasil disimpan! Terima kasih atas kontribusi Anda.")
                except Exception as e:
                    st.error(f"Gagal menyimpan feedback: {e}")

        # Display historical feedback
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="section-header">Riwayat Umpan Balik Pengguna</p>', unsafe_allow_html=True)
        if feedback_list:
            df_fb = pd.DataFrame(feedback_list)
            # Reorder columns
            df_fb.columns = ['Waktu', 'Kategori Tren', 'Rating Kualitas', 'Komentar Pengguna']
            st.dataframe(df_fb.sort_values(by='Waktu', ascending=False), use_container_width=True, hide_index=True)
        else:
            st.write("Belum ada umpan balik yang terekam.")
