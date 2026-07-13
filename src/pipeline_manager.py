import os
import logging
from src.scraper.scraper import run_auto_pipeline
from src.preprocessing.preprocess import run_preprocessing_pipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_full_pipeline(queries: list, limit_per_query: int = 5, lang: str = "id", country: str = "ID"):
    """
    Runs the full pipeline:
    1. Search & Scrape raw articles based on queries.
    2. Preprocess raw articles (cleaning, tokenization, stemming, stopword removal).
    """
    logger.info("================ STARTING FULL PIPELINE ================")
    
    # 1. Run Scraper
    raw_path = "data/raw_articles.json"
    logger.info("Step 1: Running scraper...")
    run_auto_pipeline(queries, limit_per_query=limit_per_query, output_dir="data", lang=lang, country=country)
    
    # 2. Run Preprocessor
    preprocessed_path = "data/preprocessed_articles.json"
    logger.info("Step 2: Running text preprocessing...")
    run_preprocessing_pipeline(input_path=raw_path, output_path=preprocessed_path)
    
    # 3. Run Topic Modeling & Trend Clustering
    clustered_path = "data/clustered_articles.json"
    logger.info("Step 3: Running topic modeling and trend clustering...")
    from src.modeling.topic_model import run_clustering_pipeline
    run_clustering_pipeline(input_path=preprocessed_path, output_path=clustered_path)
    
    # 4 & 5. Run AI Summarization & Final Analysis
    report_path = "data/final_summary_report.json"
    logger.info("Step 4 & 5: Running AI summarization and generating final report...")
    from src.summarizer.summary_engine import run_summarization_pipeline
    run_summarization_pipeline(input_path=clustered_path, output_path=report_path)
    
    logger.info("================ PIPELINE COMPLETED SUCCESSFULLY ================")

if __name__ == "__main__":
    # Standard queries for the project
    default_queries = [
        "FMCG keberlanjutan Indonesia",
        "pemasaran digital ritel Indonesia",
        "perubahan perilaku konsumen ritel"
    ]
    # Run the pipeline with limit 2 per query for testing
    print("Testing pipeline manager with 2 links per query...")
    run_full_pipeline(default_queries, limit_per_query=2, lang="id", country="ID")
