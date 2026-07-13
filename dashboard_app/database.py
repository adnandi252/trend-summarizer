import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("database")

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "app_database.db"))

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Returns rows as dictionary-like objects
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Projects Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            keywords TEXT NOT NULL,  -- JSON string list of keywords
            status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'scraping', 'processing', 'completed', 'failed'
            error_message TEXT,
            created_at TEXT NOT NULL,
            last_run_at TEXT
        )
    """)

    # 2. Articles Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            url TEXT,
            source TEXT,
            publish_date TEXT,
            raw_text TEXT,
            clean_text TEXT,
            trend_category TEXT DEFAULT 'Unclustered',
            cluster_id INTEGER,
            keywords TEXT, -- JSON string list of keywords
            analysis_period TEXT DEFAULT 'all',
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # 3. Summaries Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            trend_category TEXT NOT NULL,
            article_count INTEGER DEFAULT 0,
            top_keywords TEXT, -- JSON string list of keywords
            extractive_brief TEXT,
            generative_brief TEXT,
            market_opportunities TEXT, -- JSON string list of opportunities
            consumer_behavior TEXT, -- JSON string list of behavior insights
            analysis_period TEXT DEFAULT 'all',
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # 4. Feedbacks Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            trend_category TEXT NOT NULL,
            rating TEXT NOT NULL,
            comment TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Run migrations programmatically to add analysis_period column to existing tables
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN analysis_period TEXT DEFAULT 'all'")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE summaries ADD COLUMN analysis_period TEXT DEFAULT 'all'")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

# --- Project Operations ---

def create_project(name: str, description: str, keywords: List[str]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    keywords_json = json.dumps(keywords)
    
    cursor.execute(
        "INSERT INTO projects (name, description, keywords, status, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, description, keywords_json, "draft", created_at)
    )
    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def get_projects() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_project_status(project_id: int, status: str, error_message: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    last_run_at = datetime.now().isoformat() if status in ["completed", "failed"] else None
    
    if last_run_at:
        cursor.execute(
            "UPDATE projects SET status = ?, error_message = ?, last_run_at = ? WHERE id = ?",
            (status, error_message, last_run_at, project_id)
        )
    else:
        cursor.execute(
            "UPDATE projects SET status = ?, error_message = ? WHERE id = ?",
            (status, error_message, project_id)
        )
    conn.commit()
    conn.close()

def delete_project(project_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Enable foreign keys to trigger ON DELETE CASCADE
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()

# --- Articles Operations ---

def insert_articles(project_id: int, articles_list: List[Dict[str, Any]], analysis_period: str = 'all'):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First, clear any old articles for this project and period (e.g. if rerun)
    cursor.execute("DELETE FROM articles WHERE project_id = ? AND analysis_period = ?", (project_id, analysis_period))
    
    for art in articles_list:
        # Use article_keywords if present, fallback to keywords, or empty list
        kws = art.get("article_keywords") or art.get("keywords") or []
        keywords_json = json.dumps(kws)
        cursor.execute(
            """INSERT INTO articles (
                project_id, title, url, source, publish_date, raw_text, clean_text, trend_category, cluster_id, keywords, analysis_period
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project_id,
                art.get("title"),
                art.get("url"),
                art.get("source"),
                art.get("publish_date"),
                art.get("raw_text"),
                art.get("clean_text"),
                art.get("trend_category", "Unclustered"),
                art.get("cluster_id"),
                keywords_json,
                analysis_period
            )
        )
    conn.commit()
    conn.close()

def get_articles(project_id: int, search: Optional[str] = None, category: Optional[str] = None, analysis_period: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM articles WHERE project_id = ?"
    params = [project_id]
    
    if category:
        query += " AND trend_category = ?"
        params.append(category)
        
    if search:
        query += " AND (title LIKE ? OR source LIKE ?)"
        # Safe wildcard wrapping in python, preventing injection
        search_pattern = f"%{search}%"
        params.extend([search_pattern, search_pattern])
        
    if analysis_period:
        query += " AND analysis_period = ?"
        params.append(analysis_period)
        
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    
    articles = []
    for row in rows:
        d = dict(row)
        # Parse keywords JSON
        try:
            d["keywords"] = json.loads(d["keywords"]) if d.get("keywords") else []
        except Exception:
            d["keywords"] = []
        articles.append(d)
    return articles

def get_article(project_id: int, article_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE project_id = ? AND id = ?", (project_id, article_id))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    d = dict(row)
    try:
        d["keywords"] = json.loads(d["keywords"]) if d.get("keywords") else []
    except Exception:
        d["keywords"] = []
    return d

# --- Summaries Operations ---

def insert_summaries(project_id: int, summaries_by_category: Dict[str, Dict[str, Any]], analysis_period: str = 'all'):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear old summaries for this project and period
    cursor.execute("DELETE FROM summaries WHERE project_id = ? AND analysis_period = ?", (project_id, analysis_period))
    
    for cat_name, s_data in summaries_by_category.items():
        kws = json.dumps(s_data.get("top_keywords", []))
        opps = json.dumps(s_data.get("market_opportunities", []))
        cb = json.dumps(s_data.get("consumer_behavior", []))
        cursor.execute(
            """INSERT INTO summaries (
                project_id, trend_category, article_count, top_keywords, extractive_brief, generative_brief, market_opportunities, consumer_behavior, analysis_period
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                project_id,
                cat_name,
                s_data.get("article_count", 0),
                kws,
                s_data.get("extractive_brief", ""),
                s_data.get("generative_brief", ""),
                opps,
                cb,
                analysis_period
            )
        )
    conn.commit()
    conn.close()

def get_summaries(project_id: int, analysis_period: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # If no period is specified, try to find the latest period that has summaries
    if not analysis_period:
        cursor.execute("SELECT DISTINCT analysis_period FROM summaries WHERE project_id = ? ORDER BY id DESC LIMIT 1", (project_id,))
        row_period = cursor.fetchone()
        if row_period:
            analysis_period = row_period["analysis_period"]
        else:
            analysis_period = 'all'
            
    cursor.execute("SELECT * FROM summaries WHERE project_id = ? AND analysis_period = ?", (project_id, analysis_period))
    rows = cursor.fetchall()
    conn.close()
    
    report = {}
    for row in rows:
        d = dict(row)
        cat_name = d["trend_category"]
        
        try:
            top_kws = json.loads(d["top_keywords"]) if d.get("top_keywords") else []
        except Exception:
            top_kws = []
            
        try:
            opps = json.loads(d["market_opportunities"]) if d.get("market_opportunities") else []
        except Exception:
            opps = []
            
        try:
            cb = json.loads(d["consumer_behavior"]) if d.get("consumer_behavior") else []
        except Exception:
            cb = []
            
        report[cat_name] = {
            "trend_category": cat_name,
            "article_count": d["article_count"],
            "top_keywords": top_kws,
            "extractive_brief": d["extractive_brief"],
            "generative_brief": d["generative_brief"],
            "market_opportunities": opps,
            "consumer_behavior": cb,
            "analysis_period": d["analysis_period"]
        }
    return report

def get_analysis_periods(project_id: int) -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT analysis_period FROM summaries WHERE project_id = ? ORDER BY analysis_period DESC", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row["analysis_period"] for row in rows if row["analysis_period"]]

# --- Feedbacks Operations ---

def insert_feedback(project_id: int, category: str, rating: str, comment: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO feedbacks (project_id, trend_category, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)",
        (project_id, category, rating, comment, created_at)
    )
    conn.commit()
    conn.close()

def get_feedbacks(project_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedbacks WHERE project_id = ? ORDER BY created_at DESC", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
