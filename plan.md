# Master Plan: Industry Trend Summarization AI

## 1. Deskripsi Proyek
Proyek ini bertujuan untuk membangun solusi berbasis Artificial Intelligence (AI) yang berfungsi mengumpulkan, mengelompokkan, dan merangkum tren industri dari berbagai sumber publik (FMCG, Retail, Consumer Behavior) secara otomatis menjadi bentuk executive brief guna mendukung pengambilan keputusan strategis.

## 2. Referensi Arsitektur & Ketentuan
*   **Dokumen Acuan:** `image_9e7f9d.png` dan `image_9e7fa0.png`
*   **Bahasa Pemrograman Utama:** Python
*   **Daftar Tools & Library:**
    | Komponen | Teknologi |
    | :--- | :--- |
    | Scraper / Data Collection | Newspaper3k |
    | Topic Modeling & Clustering | Gensim, Scikit-learn |
    | NLP Preprocessing | NLTK / Spacy / Sastrawi |
    | Summarization (Extractive) | TextRank (Gensim / NetworkX) |
    | Summarization (Generative) | Hugging Face Transformers, OpenAI API (Opsional) |
    | Dashboard Visualization | Streamlit / Dash / FastAPI + React |

## 3. Garis Besar Struktur Folder Proyek
├── data/                  # Penyimpanan raw data & clean data
├── src/
│   ├── scraper/           # Modul pengumpulan data (Newspaper3k)
│   ├── preprocessing/     # Modul pembersihan teks
│   ├── modeling/          # Modul Topic Modeling & Clustering
│   ├── summarizer/        # Modul AI Summarization (Extractive & Generative)
│   └── dashboard/         # Kode aplikasi dashboard visualisasi
├── evaluation/            # Script untuk pengujian ROUGE Score
├── plans/                 # File detail tugas (Sub-plans)
│   ├── 01_data_pipeline.md
│   ├── 02_ai_modeling.md
│   └── 03_dashboard_eval.md
├── requirements.txt
└── plan.md                # File ini

## 4. Mekanisme Environment Project
Gunakan WSL dan dan pakai Environment Conda bernama "inference-model".