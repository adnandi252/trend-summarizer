import os
import sys
import json
import asyncio
import logging


from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("backend")

# Resolve workspace root directory to allow src imports
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Resolve local directories
DASHBOARD_APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(DASHBOARD_APP_DIR, "static")

# Load environment configuration from .env in workspace root
def load_dotenv(dotenv_path: str):
    if os.path.exists(dotenv_path):
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    os.environ[key] = val
                    logger.info(f"Loaded config from .env: {key}")

dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(dotenv_file):
    load_dotenv(dotenv_file)

# Import SQLite Database operations
import dashboard_app.database as db

# Initialize database schema on startup
try:
    db.init_db()
    logger.info("SQLite Database initialized successfully.")
except Exception as e:
    logger.critical(f"Database initialization failed: {e}", exc_info=True)

# Initialize FastAPI
app = FastAPI(
    title="TrendAI Rebuilt API",
    description="SaaS Web Backend API supporting Multi-project scraping, topic modeling, and summarization workflows.",
    version="1.0.0"
)

# CORS Policy configuration
# Determine allowed origins — include HF Spaces domains for deployment
_ALLOWED_ORIGINS = [
    "http://localhost:3000", "http://localhost:5173",
    "http://127.0.0.1:3000", "http://127.0.0.1:5173",
    "http://localhost:8001", "http://127.0.0.1:8001",
]
# Add the HF Spaces origin if running on Spaces
_HF_SPACE = os.environ.get("SPACE_HOST")
if _HF_SPACE:
    _ALLOWED_ORIGINS.append(f"https://{_HF_SPACE}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    # On HF Spaces, skip X-Frame-Options so Gradio can iframe dashboard pages;
    # CSP frame-ancestors handles framing security instead.
    if not os.environ.get("SPACE_HOST"):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Content-Security-Policy (CSP) - Allow static resources, Tailwind CDN, Google Fonts, and images
    # Build CSP — allow HF Spaces domain for frame-ancestors so Gradio can iframe dashboard pages
    hf_host = os.environ.get("SPACE_HOST", "")
    frame_ancestors = "'self'"
    if hf_host:
        frame_ancestors += f" https://{hf_host}"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https://lh3.googleusercontent.com; "
        "connect-src 'self'; "
        f"frame-ancestors {frame_ancestors};"
    )
    return response

async def run_weekly_scheduler():
    logger.info("Scheduler analisis mingguan diaktifkan.")
    while True:
        try:
            now = datetime.now()
            # Sunday is weekday 6
            if now.weekday() == 6:
                # Preceding week date range: Monday to Sunday
                start_dt = now - timedelta(days=6)
                end_dt = now
                start_date_str = start_dt.strftime("%Y-%m-%d")
                end_date_str = end_dt.strftime("%Y-%m-%d")
                period_str = f"{start_date_str} s/d {end_date_str}"
                
                projects = db.get_projects()
                for proj in projects:
                    project_id = proj["id"]
                    if proj["status"] not in ["scraping", "processing"]:
                        periods = db.get_analysis_periods(project_id)
                        if period_str not in periods:
                            logger.info(f"Penyaringan otomatis mingguan terpicu untuk proyek {project_id} periode {period_str}")
                            asyncio.create_task(
                                asyncio.to_thread(
                                    execute_analyze_task,
                                    project_id=project_id,
                                    model_source="groq",
                                    groq_model="test-1",
                                    start_date=start_date_str,
                                    end_date=end_date_str
                                )
                            )
        except Exception as e:
            logger.error(f"Kesalahan pada scheduler mingguan: {e}", exc_info=True)
        # Check every 1 hour
        await asyncio.sleep(3600)

@app.on_event("startup")
async def startup_event():
    # Reset any stuck projects from previous interrupted server runs
    try:
        conn = db.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET status = 'draft' WHERE status IN ('processing', 'scraping')")
        conn.commit()
        conn.close()
        logger.info("✓ Stuck projects have been reset to 'draft' status on startup.")
    except Exception as e:
        logger.error(f"Error resetting stuck projects on startup: {e}")

    asyncio.create_task(run_weekly_scheduler())

# --- Pydantic Data Models ---

PIPELINE_LOGS = {}

def add_pipeline_log(project_id: int, message: str):
    """Appends a timestamped message to the project's real-time console log."""
    if project_id not in PIPELINE_LOGS:
        PIPELINE_LOGS[project_id] = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    PIPELINE_LOGS[project_id].append(f"[{timestamp}] {message}")
    if len(PIPELINE_LOGS[project_id]) > 100:
        PIPELINE_LOGS[project_id].pop(0)
    logger.info(f"[Proj {project_id} Log] {message}")

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Unique name of the project")
    description: Optional[str] = Field("", max_length=500, description="Brief description of project scope")
    keywords: List[str] = Field(..., min_items=1, max_items=5, description="Search query keywords for scraping")

class ScrapeTriggerRequest(BaseModel):
    limit_per_query: int = Field(5, ge=1, le=20, description="Max number of articles to download per query")
    time_range: str = Field("any", description="Google News publish date range: any, 1d, 7d, 30d, 90d")

class AnalyzeTriggerRequest(BaseModel):
    model_source: str = Field("groq", description="Model source: local or groq")
    groq_api_key: Optional[str] = Field(None, description="Optional Groq API key for cloud summarization")
    groq_model: Optional[str] = Field(None, description="Groq model ID to use for summarization")
    start_date: Optional[str] = Field(None, description="Optional filter start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Optional filter end date (YYYY-MM-DD)")

class FeedbackCreate(BaseModel):
    trend_category: str = Field(..., min_length=3, max_length=50, description="Category of the trend being reviewed")
    rating: str = Field(..., description="Rating (e.g., Sangat Baik, Cukup Baik, Perlu Perbaikan)")
    comment: str = Field("", max_length=1000, description="Optional text feedback comment")

# --- Helper to get Project Data Directory ---

def get_project_data_dir(project_id: int) -> str:
    """Returns the path to the directory containing project-specific data JSONs."""
    p_dir = os.path.join(DASHBOARD_APP_DIR, "data", f"project_{project_id}")
    os.makedirs(p_dir, exist_ok=True)
    return p_dir

# --- Background Task Runners ---

def execute_scrape_task(project_id: int, limit_per_query: int, time_range: str):
    """Downloads articles for project keywords and saves them to project directory & SQLite."""
    try:
        db.update_project_status(project_id, "scraping")
        proj = db.get_project(project_id)
        if not proj:
            logger.error(f"Scrape task failed: Project {project_id} not found.")
            return

        add_pipeline_log(project_id, "Menghubungi Google News RSS untuk pencarian artikel...")

        keywords = json.loads(proj["keywords"])
        project_dir = get_project_data_dir(project_id)

        logger.info(f"Background scraping started for Project {project_id} ({proj['name']}).")
        
        # Import scraper from parent src module
        from src.scraper.scraper import run_auto_pipeline
        run_auto_pipeline(
            keywords, 
            limit_per_query=limit_per_query, 
            output_dir=project_dir, 
            lang="id", 
            country="ID",
            time_range=time_range,
            log_callback=lambda msg: add_pipeline_log(project_id, msg)
        )
        
        # Load raw articles JSON and save to SQLite
        raw_path = os.path.join(project_dir, "raw_articles.json")
        if os.path.exists(raw_path):
            with open(raw_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)
            db.insert_articles(project_id, articles)
            add_pipeline_log(project_id, f"✓ Berhasil menyimpan {len(articles)} artikel ke database SQLite lokal.")
            db.update_project_status(project_id, "draft")
        else:
            raise FileNotFoundError("Raw articles JSON file was not generated.")
            
    except Exception as e:
        db.update_project_status(project_id, "failed", str(e))
        add_pipeline_log(project_id, f"PROSES SCRAPING GAGAL: {e}")
        logger.error(f"Scrape task failed for Project {project_id}: {e}", exc_info=True)


def execute_analyze_task(project_id: int, model_source: str = "local", groq_api_key: str = None, groq_model: str = None, start_date: str = None, end_date: str = None):
    """Runs preprocessing, topic modeling, and T5/Groq summarization stages for a specific project."""
    try:
        db.update_project_status(project_id, "processing")
        proj = db.get_project(project_id)
        if not proj:
            logger.error(f"Analysis task failed: Project {project_id} not found.")
            return

        # Determine the name of the analysis period
        analysis_period = f"{start_date} s/d {end_date}" if (start_date and end_date) else "all"

        if project_id not in PIPELINE_LOGS:
            PIPELINE_LOGS[project_id] = []
        add_pipeline_log(project_id, "Inisialisasi analisis kluster topik dan peringkasan AI...")

        project_dir = get_project_data_dir(project_id)
        raw_path = os.path.join(project_dir, "raw_articles.json")
        preprocessed_path = os.path.join(project_dir, "preprocessed_articles.json")
        clustered_path = os.path.join(project_dir, "clustered_articles.json")
        report_path = os.path.join(project_dir, "final_summary_report.json")

        # Fallback: if raw_articles JSON was cleaned up, dump from database first
        if not os.path.exists(raw_path):
            add_pipeline_log(project_id, "Memulihkan artikel terunduh dari database relasional...")
            articles = db.get_articles(project_id)
            if not articles:
                raise FileNotFoundError("No articles scraped for this project. Scraping must run first.")
            os.makedirs(project_dir, exist_ok=True)
        else:
            with open(raw_path, 'r', encoding='utf-8') as f:
                articles = json.load(f)

        # Filter articles by date range if specified
        if start_date or end_date:
            from email.utils import parsedate_to_datetime
            
            def parse_date(date_str):
                if not date_str:
                    return None
                try:
                    return parsedate_to_datetime(date_str)
                except Exception:
                    pass
                try:
                    clean_str = date_str
                    if clean_str.endswith("Z"):
                        clean_str = clean_str[:-1]
                    return datetime.fromisoformat(clean_str)
                except Exception:
                    pass
                for fmt in ("%Y-%m-%d", "%d %b %Y", "%Y/%m/%d"):
                    try:
                        return datetime.strptime(date_str, fmt)
                    except Exception:
                        pass
                return None

            filtered_articles = []
            parsed_start = parse_date(start_date) if start_date else None
            parsed_end = parse_date(end_date) if end_date else None
            
            # Make naive for safe comparison
            if parsed_start and parsed_start.tzinfo:
                parsed_start = parsed_start.replace(tzinfo=None)
            if parsed_end and parsed_end.tzinfo:
                parsed_end = parsed_end.replace(tzinfo=None)

            for art in articles:
                pub_date = parse_date(art.get("publish_date"))
                if pub_date:
                    if pub_date.tzinfo:
                        pub_date = pub_date.replace(tzinfo=None)
                    
                    if parsed_start and pub_date < parsed_start:
                        continue
                    if parsed_end and pub_date > parsed_end:
                        continue
                filtered_articles.append(art)
                
            add_pipeline_log(project_id, f"Menyaring berita berdasarkan tanggal: {start_date or 'Awal'} s/d {end_date or 'Akhir'}")
            add_pipeline_log(project_id, f"Menyaring berita: {len(articles)} -> {len(filtered_articles)} artikel dalam periode.")
            articles = filtered_articles
            
            if not articles:
                raise ValueError(f"Tidak ada berita yang ditemukan dalam rentang tanggal {start_date or 'Awal'} s/d {end_date or 'Akhir'}.")

        # Save the filtered/restored articles list back to raw_path
        with open(raw_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4, ensure_ascii=False)

        logger.info(f"Background analysis started for Project {project_id} ({proj['name']}).")
        
        # 1. Preprocessing
        add_pipeline_log(project_id, "Langkah 1/3: NLP Preprocessing (Tokenisasi, Stopwords, Stemming Sastrawi)...")
        from src.preprocessing.preprocess import run_preprocessing_pipeline
        run_preprocessing_pipeline(input_path=raw_path, output_path=preprocessed_path)
        add_pipeline_log(project_id, "✓ Preprocessing berhasil. Kata dasar telah diindeks.")
        
        # 2. Topic Modeling & Clustering
        add_pipeline_log(project_id, "Langkah 2/3: Melatih KMeans & Klasifikasi Kata Kunci Kategori...")
        from src.modeling.topic_model import run_clustering_pipeline
        run_clustering_pipeline(input_path=preprocessed_path, output_path=clustered_path)
        add_pipeline_log(project_id, "✓ Klusterisasi KMeans berhasil dipetakan.")
        
        # 3. AI Summarization (Extractive & Generative T5/Groq)
        add_pipeline_log(project_id, "Langkah 3/3: Memicu model Generative Ringkasan & PageRank TextRank...")
        from src.summarizer.summary_engine import run_summarization_pipeline
        run_summarization_pipeline(
            input_path=clustered_path,
            output_path=report_path,
            model_source=model_source,
            groq_api_key=groq_api_key,
            groq_model=groq_model
        )
        add_pipeline_log(project_id, "✓ Peringkasan Generasi Model selesai.")

        # 4. Read clustered articles output and write to SQLite
        if os.path.exists(clustered_path):
            with open(clustered_path, 'r', encoding='utf-8') as f:
                clustered_arts = json.load(f)
            db.insert_articles(project_id, clustered_arts, analysis_period=analysis_period)
            
        # 5. Read summary report output and write to SQLite
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as f:
                summaries = json.load(f)
            db.insert_summaries(project_id, summaries, analysis_period=analysis_period)
            
        db.update_project_status(project_id, "completed")
        add_pipeline_log(project_id, "STATUS: SELURUH PROSES ANALISIS SELESAI! Dashboard terupdate.")
        logger.info(f"Analysis completed successfully for Project {project_id}.")
        
    except Exception as e:
        db.update_project_status(project_id, "failed", str(e))
        add_pipeline_log(project_id, f"PROSES ANALISIS GAGAL: {e}")
        logger.error(f"Analysis task failed for Project {project_id}: {e}", exc_info=True)


# --- External News Feed API (For Discovery tab or general searches) ---

NEWS_CATEGORIES = {
    "terbaru": {
        "queries": ["breaking news Indonesia", "berita terkini", "headline news"],
        "label": "Terbaru",
        "color": "#4f46e5"
    },
    "teknologi": {
        "queries": ["teknologi Indonesia", "tech news", "digital Indonesia", "AI teknologi"],
        "label": "Teknologi",
        "color": "#3b82f6"
    },
    "bisnis": {
        "queries": ["bisnis Indonesia ekonomi", "business news", "ekonomi digital", "startup Indonesia"],
        "label": "Bisnis & Ekonomi",
        "color": "#10b981"
    },
    "olahraga": {
        "queries": ["olahraga Indonesia", "sports news Indonesia", "sepak bola Indonesia"],
        "label": "Olahraga",
        "color": "#f59e0b"
    },
    "hiburan": {
        "queries": ["hiburan Indonesia", "entertainment news", "film musik Indonesia", "selebriti"],
        "label": "Hiburan",
        "color": "#ec4899"
    },
    "kesehatan": {
        "queries": ["kesehatan Indonesia", "health news", "medis kesehatan", "gaya hidup sehat"],
        "label": "Kesehatan",
        "color": "#14b8a6"
    },
    "sains": {
        "queries": ["sains Indonesia", "science news", "penelitian teknologi", "lingkungan"],
        "label": "Sains & Lingkungan",
        "color": "#8b5cf6"
    },
    "dunia": {
        "queries": ["world news", "international news", "global news", "berita dunia"],
        "label": "Dunia Internasional",
        "color": "#f97316"
    }
}

@app.get("/api/news/categories")
def api_get_news_categories():
    """Returns available news categories."""
    categories = []
    for key, cat in NEWS_CATEGORIES.items():
        categories.append({
            "id": key,
            "label": cat["label"],
            "color": cat["color"]
        })
    return categories


@app.get("/api/news/trending")
def api_get_trending_news(
    category: str = Query("terbaru", description="News category ID"),
    search: Optional[str] = Query(None, min_length=2, max_length=100, description="Custom search query"),
    limit: int = Query(12, ge=1, le=50, description="Number of articles to fetch"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Fetches the latest news articles from Google News RSS based on category or search query."""
    from src.scraper.scraper import search_articles
    try:
        if search:
            custom_query = search.strip()
            articles = search_articles(custom_query, limit=limit + offset, lang="id", country="ID", time_range="7d")
        elif category in NEWS_CATEGORIES:
            cat_data = NEWS_CATEGORIES[category]
            all_articles = []
            seen_urls = set()
            per_query_limit = max(1, (limit + offset) // len(cat_data["queries"]) + 1)
            
            for query in cat_data["queries"]:
                results = search_articles(query, limit=per_query_limit, lang="id", country="ID", time_range="7d")
                for art in results:
                    url = art.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_articles.append(art)
            articles = all_articles
        else:
            articles = search_articles("berita terkini Indonesia", limit=limit + offset, lang="id", country="ID", time_range="7d")
        
        total_count = len(articles)
        paginated = articles[offset:offset + limit]
        
        result = []
        for art in paginated:
            result.append({
                "title": art.get("title", "No Title"),
                "url": art.get("url", ""),
                "source": art.get("source", "Unknown Source"),
                "publish_date": art.get("publish_date", ""),
                "query": art.get("query", ""),
                "snippet": art.get("title", "")
            })
        
        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "articles": result,
            "category": category
        }
    except Exception as e:
        logger.error(f"Failed to fetch news: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil berita: {str(e)}"
        )


# --- Project CRUD Routing ---

@app.post("/api/projects", status_code=status.HTTP_201_CREATED)
def api_create_project(payload: ProjectCreate):
    """Creates a new topic tracking project in the SQLite database."""
    try:
        project_id = db.create_project(payload.name, payload.description, payload.keywords)
        new_project = db.get_project(project_id)
        return new_project
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project due to database write failure."
        )

@app.get("/api/projects")
def api_get_projects():
    """Retrieves all projects from the database."""
    return db.get_projects()

@app.get("/api/projects/{project_id}")
def api_get_project_detail(project_id: int):
    """Retrieves metadata of a specific project including articles count."""
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    
    articles = db.get_articles(project_id)
    proj_dict = dict(proj)
    proj_dict["article_count"] = len(articles)
    return proj_dict

@app.delete("/api/projects/{project_id}")
def api_delete_project(project_id: int):
    """Deletes a project and all cascaded database records."""
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    
    try:
        db.delete_project(project_id)
        # Clean up project disk directories
        project_dir = get_project_data_dir(project_id)
        if os.path.exists(project_dir):
            import shutil
            shutil.rmtree(project_dir, ignore_errors=True)
        return {"status": "success", "message": f"Project {project_id} deleted successfully."}
    except Exception as e:
        logger.error(f"Failed to delete project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project database entries."
        )


# --- Pipeline Orchestrator Routing ---

@app.post("/api/projects/{project_id}/scrape", status_code=status.HTTP_202_ACCEPTED)
def api_trigger_scrape(project_id: int, payload: ScrapeTriggerRequest, background_tasks: BackgroundTasks):
    """Triggers news scraping for a specific project's keywords in the background."""
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        
    if proj["status"] in ["scraping", "processing"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project pipeline is busy. Wait for active process to complete."
        )
        
    PIPELINE_LOGS[project_id] = []
    add_pipeline_log(project_id, "Inisialisasi penarikan berita...")
    background_tasks.add_task(execute_scrape_task, project_id, payload.limit_per_query, payload.time_range)
    return {"status": "running", "message": "Scrape task submitted to background queue."}

@app.post("/api/projects/{project_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
def api_trigger_analysis(
    project_id: int,
    background_tasks: BackgroundTasks,
    payload: Optional[AnalyzeTriggerRequest] = None
):
    """Triggers cleaning, topic modeling and generative T5/Groq summarization in the background."""
    payload = payload or AnalyzeTriggerRequest()
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        
    if proj["status"] in ["scraping", "processing"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project pipeline is busy. Wait for active process to complete."
        )
        
    PIPELINE_LOGS[project_id] = []
    add_pipeline_log(project_id, "Inisialisasi analisis kluster topik dan peringkasan AI...")
    background_tasks.add_task(execute_analyze_task, project_id, payload.model_source, payload.groq_api_key, payload.groq_model, payload.start_date, payload.end_date)
    return {"status": "running", "message": "Analysis task submitted to background queue."}

@app.get("/api/projects/{project_id}/logs")
def api_get_project_logs(project_id: int):
    """Retrieves execution logs for the specified project's pipeline."""
    return PIPELINE_LOGS.get(project_id, [])


# --- Project Specific Data Routing ---

@app.get("/api/projects/{project_id}/trends")
def api_get_project_trends(project_id: int, period: Optional[str] = Query(None)):
    """Retrieves summaries, keywords, and articles grouped by category for the specified project."""
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        
    trends = db.get_summaries(project_id, analysis_period=period)
    if not trends:
         # Return empty summaries representation so UI knows no analysis has run yet
         return {}
    
    # Determine active period name to query corresponding articles
    active_period = list(trends.values())[0]["analysis_period"] if trends else period
    
    # Fetch articles grouped by trend_category and attach them to the trends response
    articles = db.get_articles(project_id, analysis_period=active_period)
    articles_by_category = {}
    for art in articles:
        cat = art.get("trend_category", "Unclustered")
        if cat not in articles_by_category:
            articles_by_category[cat] = []
        articles_by_category[cat].append({
            "title": art.get("title"),
            "url": art.get("url"),
            "source": art.get("source"),
            "publish_date": art.get("publish_date")
        })
    
    for cat_name, cat_data in trends.items():
        cat_data["articles"] = articles_by_category.get(cat_name, [])
    
    return trends

@app.get("/api/projects/{project_id}/periods")
def api_get_project_periods(project_id: int):
    """Retrieves all weekly analysis periods saved in the database for the project."""
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return db.get_analysis_periods(project_id)

@app.get("/api/projects/{project_id}/articles")
def api_get_project_articles(
    project_id: int,
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    category: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """Retrieves list of articles for the specified project with text/category filters."""
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        
    articles = db.get_articles(project_id, search=search, category=category)
    total_count = len(articles)
    paginated = articles[offset : offset + limit]
    
    list_representation = []
    for art in paginated:
        list_representation.append({
            "id": art.get("id"),
            "title": art.get("title"),
            "url": art.get("url"),
            "source": art.get("source"),
            "publish_date": art.get("publish_date"),
            "trend_category": art.get("trend_category", "Unclustered"),
            "keywords": art.get("keywords", [])
        })
        
    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "articles": list_representation
    }

@app.get("/api/projects/{project_id}/articles/{article_id}")
def api_get_project_article_detail(project_id: int, article_id: int):
    """Retrieves full article details (raw & cleaned text) for the specified project and ID."""
    art = db.get_article(project_id, article_id)
    if not art:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found under project {project_id}."
        )
    return art

@app.get("/api/projects/{project_id}/feedback")
def api_get_project_feedback(project_id: int):
    """Retrieves user feedback reviews history for the specified project."""
    return db.get_feedbacks(project_id)

@app.post("/api/projects/{project_id}/feedback", status_code=status.HTTP_201_CREATED)
def api_submit_project_feedback(project_id: int, payload: FeedbackCreate):
    """Submits and persists a user feedback entry for a specific project summary."""
    proj = db.get_project(project_id)
    if not proj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
        
    try:
        db.insert_feedback(project_id, payload.trend_category, payload.rating, payload.comment)
        return {"status": "success", "message": "Feedback submitted successfully."}
    except Exception as e:
        logger.error(f"Failed to save project feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save feedback to database."
        )

@app.get("/api/health")
def read_health():
    """Health check status endpoint."""
    return {
        "app": "TrendAI Rebuilt API Backend",
        "status": "active",
        "timestamp": datetime.now().isoformat()
    }


# --- Frontend Static Routes ---

@app.get("/", response_class=FileResponse)
def serve_index():
    """Serves the main dashboard page."""
    return FileResponse(os.path.join(STATIC_DIR, "dashboard.html"))

@app.get("/dashboard.html", response_class=FileResponse)
def serve_dashboard():
    """Serves the main dashboard page."""
    return FileResponse(os.path.join(STATIC_DIR, "dashboard.html"))

@app.get("/trend_discovery.html", response_class=FileResponse)
def serve_trend_discovery():
    """Serves the trend details page."""
    return FileResponse(os.path.join(STATIC_DIR, "trend_discovery.html"))

@app.get("/executive_brief.html", response_class=FileResponse)
def serve_executive_brief():
    """Serves the printable report page."""
    return FileResponse(os.path.join(STATIC_DIR, "executive_brief.html"))

@app.get("/news_management.html", response_class=FileResponse)
def serve_news_management():
    """Serves the news management page."""
    return FileResponse(os.path.join(STATIC_DIR, "news_management.html"))

# Mount Static Files for js, css, etc.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
