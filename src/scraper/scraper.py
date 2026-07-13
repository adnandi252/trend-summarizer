import os
import json
import logging
import urllib.parse
from datetime import datetime
import feedparser
from newspaper import Article, Config
from googlenewsdecoder import gnewsdecoder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Scraper configuration
CONFIG = Config()
CONFIG.browser_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36"
)
CONFIG.request_timeout = 15

def get_source_name(entry, fallback_url: str) -> str:
    """
    Get the name of the source from feed entry or parse domain as fallback.
    """
    if hasattr(entry, 'source') and 'title' in entry.source:
        return entry.source.title
    try:
        parsed_uri = urllib.parse.urlparse(fallback_url)
        return parsed_uri.netloc.replace('www.', '')
    except Exception:
        return "Unknown Source"

def search_articles(query: str, limit: int = 10, lang: str = "id", country: str = "ID", time_range: str = "any") -> list:
    """
    Search articles from Google News RSS based on a query, localized to lang/country.
    Returns a list of dicts containing metadata (title, link, published, source).
    """
    adjusted_query = query
    if time_range and time_range != "any":
        adjusted_query = f"{query} when:{time_range}"
        
    encoded_query = urllib.parse.quote(adjusted_query)
    ceid = f"{country}:{lang}"
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl={lang}&gl={country}&ceid={ceid}"
    
    logger.info(f"Searching Google News RSS for query: '{adjusted_query}' (lang: {lang}, country: {country})...")
    feed = feedparser.parse(rss_url)
    
    articles = []
    for entry in feed.entries[:limit]:
        title = getattr(entry, 'title', 'No Title')
        link = getattr(entry, 'link', '')
        published = getattr(entry, 'published', '')
        source = get_source_name(entry, link)
        
        if link:
            articles.append({
                "title": title,
                "url": link,
                "publish_date": published,
                "source": source,
                "query": query
            })
            
    logger.info(f"Found {len(articles)} article links for query: '{query}'.")
    return articles

def scrape_article(url: str, lang: str = "id") -> str:
    """
    Scrapes the full text of an article using Newspaper3k with a specific language setting.
    """
    logger.info(f"Scraping content from URL: {url} (lang: {lang})")
    try:
        # Create a dynamic config to pass the specific language
        config = Config()
        config.browser_user_agent = CONFIG.browser_user_agent
        config.request_timeout = CONFIG.request_timeout
        config.language = lang  # e.g., 'id' for Indonesian
        
        article = Article(url, config=config)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        logger.warning(f"Failed to scrape article from {url}: {e}")
        return ""

def run_auto_pipeline(queries: list, limit_per_query: int = 5, output_dir: str = "data", lang: str = "id", country: str = "ID", time_range: str = "any", log_callback = None) -> str:
    """
    Runs the automated search and scrape pipeline for a list of queries.
    Saves the results to raw_articles.json.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "raw_articles.json")
    
    if log_callback:
        log_callback(f"Memulai pipeline penarikan berita untuk {len(queries)} kata kunci.")
        log_callback(f"Rentang waktu terbit berita: {time_range if time_range != 'any' else 'Semua Waktu'}")
    
    # Load existing articles if file exists to prevent overwriting new runs
    all_articles = []
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                all_articles = json.load(f)
            logger.info(f"Loaded {len(all_articles)} existing articles from {output_path}")
            if log_callback:
                log_callback(f"Ditemukan {len(all_articles)} artikel pra-eksis di arsip lokal.")
        except Exception as e:
            logger.error(f"Error loading existing raw_articles.json: {e}")
            
    existing_urls = {art["url"] for art in all_articles if "url" in art}
    
    scraped_count = 0
    for query in queries:
        if log_callback:
            log_callback(f"Mencari query: '{query}' di Google News...")
        discovered_articles = search_articles(query, limit=limit_per_query, lang=lang, country=country, time_range=time_range)
        if log_callback:
            log_callback(f"Menemukan {len(discovered_articles)} artikel potensial untuk query: '{query}'")
            
        for art in discovered_articles:
            google_url = art["url"]
            
            # Decode the Google News redirect URL to the direct article URL
            decoded_url = google_url
            try:
                if log_callback:
                    log_callback(f"Mendekode rujukan URL Google News...")
                decoded_data = gnewsdecoder(google_url)
                if decoded_data.get("status"):
                    decoded_url = decoded_data["decoded_url"]
                    logger.info(f"Decoded Google News URL to: {decoded_url}")
                else:
                    logger.warning(f"Could not decode Google News URL, using original: {google_url}")
            except Exception as e:
                logger.error(f"Error decoding Google News URL: {e}")
            
            art["url"] = decoded_url
            if decoded_url in existing_urls:
                logger.info(f"Skipping already scraped URL: {decoded_url}")
                if log_callback:
                    log_callback(f"Melewati URL (sudah pernah diunduh): {decoded_url[:60]}...")
                continue
                
            if log_callback:
                log_callback(f"Mengunduh teks lengkap dari: {art['source']} ({decoded_url[:50]}...)")
            raw_text = scrape_article(decoded_url, lang=lang)
            # Only save articles that have non-empty content
            if raw_text and len(raw_text.strip()) > 150:
                art["raw_text"] = raw_text.strip()
                art["scraped_at"] = datetime.now().isoformat()
                all_articles.append(art)
                existing_urls.add(decoded_url)
                scraped_count += 1
                if log_callback:
                    log_callback(f"✓ Berhasil mengunduh artikel: \"{art['title'][:45]}...\"")
            else:
                logger.info(f"Skipped URL due to empty or too short content: {decoded_url}")
                if log_callback:
                    log_callback(f"⚠ Skip artikel (konten kosong/terlalu pendek): {decoded_url[:50]}...")
                
    # Assign sequential IDs to all articles before saving
    for idx, art in enumerate(all_articles, 1):
        ordered_art = {"id": idx}
        ordered_art.update({k: v for k, v in art.items() if k != "id"})
        all_articles[idx - 1] = ordered_art
 
    # Save back to JSON
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, indent=4, ensure_ascii=False)
        logger.info(f"Pipeline finished. Successfully scraped {scraped_count} new articles. Total saved: {len(all_articles)} articles.")
        if log_callback:
            log_callback(f"Selesai! {scraped_count} berita baru ditambahkan. Total database proyek memiliki {len(all_articles)} berita.")
    except Exception as e:
        logger.error(f"Failed to write results to {output_path}: {e}")
        if log_callback:
            log_callback(f"❌ Gagal menulis hasil ke file lokal: {e}")
        
    return output_path

if __name__ == "__main__":
    # Test queries focused on Indonesian industry trends
    test_queries = [
        "FMCG keberlanjutan Indonesia",
        "pemasaran digital ritel Indonesia",
        "perubahan perilaku konsumen ritel"
    ]
    print("Starting pipeline test focused on Indonesian news...")
    path = run_auto_pipeline(test_queries, limit_per_query=4, lang="id", country="ID")
    print(f"Test completed. Output path: {path}")
