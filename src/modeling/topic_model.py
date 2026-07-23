import os
import json
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Reference keywords for each target category in Indonesian and English
# Only 3 target categories as required by the dashboard
REFERENCE_KEYWORDS = {
    "Sustainability": [
        "keberlanjutan", "lingkungan", "hijau", "eco", "ramah", "sustainability", 
        "sampah", "plastik", "daur", "ulang", "emisi", "karbon", "energi", "green",
        "esg", "sosial", "tanggung", "jawab", "limbah", "pohon", "alam", "bumi",
        "iklim", "klimat", "berkelanjutan", "organik", "biodegradable", "ramah lingkungan",
        "terbarukan", "polusi", "konservasi", "net zero", "carbon", "recycle", "eco-friendly"
    ],
    "Digital Marketing": [
        "marketing", "digital", "pemasaran", "kampanye", "campaign", "iklan", "ads",
        "media", "sosial", "konten", "promosi", "brand", "influencer", "tiktok",
        "instagram", "facebook", "youtube", "branding", "strategi", "pesan",
        "kreatif", "audiens", "target", "engagement", "views", "followers", "seo",
        "content", "marketing strategy", "social media", "digital campaign"
    ],
    "Consumer Behavior Shift": [
        "perilaku", "konsumen", "perubahan", "shift", "belanja", "online", "toko",
        "fisik", "e-commerce", "transaksi", "pasar", "digitalisasi", "beli",
        "kebutuhan", "tren", "shopee", "tokopedia", "gaya", "hidup", "masyarakat",
        "ekonomi", "keuangan", "bayar", "cashless", "dompet", "mudah", "konsumer",
        "kebiasaan", "pola", "pengeluaran", "daya beli", "preferensi", "pergeseran"
    ]
}

class TrendClustering:
    def __init__(self, n_clusters=3):
        self.n_clusters = n_clusters
        # Use a slightly wider TF-IDF setting to capture meaningful bigrams as well
        self.vectorizer = TfidfVectorizer(max_df=0.85, min_df=2, ngram_range=(1, 2))
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.cluster_to_category = {}
        self.category_keywords = {}

    def fit_predict(self, documents: list) -> list:
        """
        Fits TF-IDF and K-Means, then computes category mapping.
        """
        num_docs = len(documents)
        if num_docs == 0:
            return []

        # Adjust clusters
        self.n_clusters = min(self.n_clusters, num_docs)

        # Fallback to direct heuristics if we have very few documents to cluster reliably
        if num_docs < 3:
            logger.info("Too few documents for K-Means. Using heuristic mapping...")
            self.cluster_to_category = {}
            self.category_keywords = {cat: [] for cat in REFERENCE_KEYWORDS.keys()}
            
            # Fit a simple vectorizer to extract keyword ranks
            self.vectorizer = TfidfVectorizer(max_df=1.0, min_df=1, ngram_range=(1, 2))
            try:
                self.vectorizer.fit(documents)
            except Exception:
                pass
                
            labels = []
            categories = list(REFERENCE_KEYWORDS.keys())
            for idx, doc in enumerate(documents):
                # Simple rule-based count matching
                words = doc.lower().split()
                scores = []
                for cat in categories:
                    match_count = sum(1 for w in words if w in REFERENCE_KEYWORDS[cat])
                    scores.append(match_count)
                best_cat_idx = np.argmax(scores)
                best_cat = categories[best_cat_idx]
                
                # Assign cluster ID as its index
                self.cluster_to_category[idx] = best_cat
                # Simple top words of document as category keywords
                self.category_keywords[best_cat] = list(set(words))[:15]
                labels.append(idx)
                
            return labels

        # Standard clustering path
        logger.info(f"Vectorizing {num_docs} documents...")
        # Fallback for vocabulary pruning
        try:
            self.vectorizer = TfidfVectorizer(max_df=0.85, min_df=2, ngram_range=(1, 2))
            tfidf_matrix = self.vectorizer.fit_transform(documents)
        except ValueError:
            logger.warning("TF-IDF min_df=2 failed. Falling back to min_df=1...")
            self.vectorizer = TfidfVectorizer(max_df=0.85, min_df=1, ngram_range=(1, 2))
            tfidf_matrix = self.vectorizer.fit_transform(documents)
        
        logger.info(f"Clustering into {self.n_clusters} clusters...")
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        cluster_labels = self.kmeans.fit_predict(tfidf_matrix)
        
        # Calculate cluster-to-category mapping
        self._map_clusters_to_categories()
        
        return cluster_labels.tolist()

    def _map_clusters_to_categories(self):
        """
        Maps each cluster to a unique target category based on TF-IDF centroid weights.
        Guarantees a 1-to-1 mapping using a greedy matching algorithm.
        """
        feature_names = self.vectorizer.get_feature_names_out()
        centroids = self.kmeans.cluster_centers_
        
        # 1. Compute similarity matrix (n_clusters x n_categories)
        categories = list(REFERENCE_KEYWORDS.keys())
        score_matrix = np.zeros((self.n_clusters, len(categories)))
        
        for c in range(self.n_clusters):
            # Sort term indices by their weight in the cluster centroid
            sorted_indices = np.argsort(centroids[c])[::-1]
            
            # Map word string to its centroid weight
            word_weights = {feature_names[i]: centroids[c][i] for i in sorted_indices if centroids[c][i] > 0}
            
            for cat_idx, cat in enumerate(categories):
                score = 0.0
                ref_words = REFERENCE_KEYWORDS[cat]
                for ref_word in ref_words:
                    # Match single terms or sub-terms in bigrams
                    for word, weight in word_weights.items():
                        if ref_word in word.split():
                            score += weight
                score_matrix[c, cat_idx] = score
                
        logger.info(f"Similarity Score Matrix (Clusters vs Categories):\n{score_matrix}")
        
        # 2. Greedy 1-to-1 matching
        remaining_clusters = list(range(self.n_clusters))
        remaining_categories = list(range(len(categories)))
        self.cluster_to_category = {}
        
        while remaining_clusters and remaining_categories:
            max_val = -1
            best_c = -1
            best_cat_idx = -1
            
            # Find the highest score among remaining pairs
            for c in remaining_clusters:
                for cat_idx in remaining_categories:
                    if score_matrix[c, cat_idx] > max_val:
                        max_val = score_matrix[c, cat_idx]
                        best_c = c
                        best_cat_idx = cat_idx
                        
            cat_name = categories[best_cat_idx]
            self.cluster_to_category[best_c] = cat_name
            logger.info(f"Mapped Cluster {best_c} to Category '{cat_name}' (Score: {max_val:.4f})")
            
            remaining_clusters.remove(best_c)
            remaining_categories.remove(best_cat_idx)
            
        # 3. Handle default fallbacks if mapping is not fully populated (e.g. empty inputs)
        for c in range(self.n_clusters):
            if c not in self.cluster_to_category:
                # Assign next unused category
                unused = [cat for cat in categories if cat not in self.cluster_to_category.values()]
                self.cluster_to_category[c] = unused[0] if unused else categories[0]
                logger.info(f"Fallback Mapped Cluster {c} to Category '{self.cluster_to_category[c]}'")

        # 4. Extract keywords per category based on mapped cluster centroids
        for c, cat in self.cluster_to_category.items():
            sorted_indices = np.argsort(centroids[c])[::-1]
            top_words = [feature_names[i] for i in sorted_indices[:15]]
            self.category_keywords[cat] = top_words
            logger.info(f"Top keywords for Category '{cat}': {top_words[:8]}")

    def get_article_keywords(self, doc_text: str, top_n=8) -> list:
        """
        Extracts top keywords specific to an individual article using its TF-IDF representation.
        """
        if not doc_text:
            return []
        tfidf_vec = self.vectorizer.transform([doc_text])
        feature_names = self.vectorizer.get_feature_names_out()
        
        # Get tfidf weights for non-zero features
        non_zero_indices = tfidf_vec.nonzero()[1]
        words_weights = [(feature_names[i], tfidf_vec[0, i]) for i in non_zero_indices]
        
        # Sort by weight descending
        sorted_words = sorted(words_weights, key=lambda x: x[1], reverse=True)
        return [word for word, weight in sorted_words[:top_n]]


def run_clustering_pipeline(input_path: str = "data/preprocessed_articles.json", output_path: str = "data/clustered_articles.json", summary_path: str = "data/clustering_summary.json") -> str:
    """
    Loads preprocessed dataset, applies clustering, maps clusters to trends,
    assigns keywords, and saves the clustered dataset.
    """
    logger.info(f"Loading preprocessed dataset from: {input_path}")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file {input_path} does not exist.")
        
    with open(input_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
        
    # Extract clean text for clustering
    documents = [art.get("clean_text", "") for art in articles]
    
    # Run clustering model
    model = TrendClustering(n_clusters=3)
    labels = model.fit_predict(documents)
    
    logger.info("Applying labels and keywords to articles...")
    clustered_articles = []
    category_counts = {cat: 0 for cat in REFERENCE_KEYWORDS.keys()}
    
    for art, label in zip(articles, labels):
        trend_cat = model.cluster_to_category[label]
        category_counts[trend_cat] += 1
        
        # Extract article-specific keywords
        art_keywords = model.get_article_keywords(art.get("clean_text", ""), top_n=8)
        
        new_art = art.copy()
        new_art["cluster_id"] = label
        new_art["trend_category"] = trend_cat
        new_art["cluster_keywords"] = model.category_keywords[trend_cat][:8]
        new_art["article_keywords"] = art_keywords
        
        clustered_articles.append(new_art)
        
    # Save clustered articles dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(clustered_articles, f, indent=4, ensure_ascii=False)
        logger.info(f"Clustered dataset successfully saved to: {output_path}")
    except Exception as e:
        logger.error(f"Failed to save clustered dataset: {e}")
        raise e
        
    # Save summary metadata
    summary = {
        "category_counts": category_counts,
        "cluster_mapping": {str(k): v for k, v in model.cluster_to_category.items()},
        "category_keywords": model.category_keywords
    }
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=4, ensure_ascii=False)
        logger.info(f"Clustering summary metadata saved to: {summary_path}")
    except Exception as e:
        logger.error(f"Failed to save summary metadata: {e}")
        
    return output_path

if __name__ == "__main__":
    test_input = "data/preprocessed_articles.json"
    test_output = "data/clustered_articles.json"
    if os.path.exists(test_input):
        print("\nRunning clustering pipeline on preprocessed_articles.json...")
        run_clustering_pipeline(test_input, test_output)
    else:
        # Dry-run on dummy data
        print("Preprocessed dataset not found. Testing on dummy data:")
        dummy_docs = [
            "sustainability eco friendly fmcg ramah lingkungan daur ulang plastik sampah",
            "digital marketing campaign sosial media promosi iklan influencer instagram",
            "perilaku konsumen belanja online e-commerce shopee tokopedia transaksi cashless",
            "produk hijau energi terbarukan keberlanjutan emisi karbon bumi",
            "iklan tiktok facebook ads pemasaran konten branding audiens target"
        ]
        clustering = TrendClustering(n_clusters=3)
        labels = clustering.fit_predict(dummy_docs)
        for doc, label in zip(dummy_docs, labels):
            cat = clustering.cluster_to_category[label]
            kw = clustering.get_article_keywords(doc, top_n=3)
            print(f"Doc: '{doc}' => Cluster {label} => Category '{cat}' => Keywords: {kw}")
