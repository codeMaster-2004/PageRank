import os

# Project directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INDEX_DIR = os.path.join(BASE_DIR, 'index')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

# Create directories if they don't exist
for directory in [DATA_DIR, INDEX_DIR, RESULTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Crawler settings (Gulnaaz's component)
CRAWLER_CONFIG = {
    'category': 'Computer_science',  # Wikipedia category to crawl
    'max_pages': 500,  # Maximum pages to crawl
    'language': 'en',  # Wikipedia language
    'output_file': os.path.join(DATA_DIR, 'crawled_pages.json'),
    'graph_file': os.path.join(DATA_DIR, 'page_graph.json'),
}

# PageRank settings (Kundan's component)
PAGERANK_CONFIG = {
    'damping_factor': 0.85,  # Standard PageRank damping factor
    'convergence_threshold': 1e-6,  # L1 norm threshold for convergence
    'max_iterations': 100,  # Maximum iterations before forcing stop
    'output_file': os.path.join(RESULTS_DIR, 'pagerank_scores.pkl'),
    'output_json': os.path.join(RESULTS_DIR, 'pagerank_scores.json'),
}
EVALUATOR_CONFIG = {
    'test_queries': [
        'machine learning',
        'artificial intelligence',
        'graph algorithms',
        'neural networks',
        'deep learning',
        'data structures',
        'algorithms',
        'computer vision',
        'natural language processing',
        'database systems',
    ],
    'ndcg_k': 10,  # Calculate NDCG@10
    'relevance_file': os.path.join(RESULTS_DIR, 'relevance_judgments.json'),
}

# Indexer settings (Teja's component)
INDEXER_CONFIG = {
    'index_file': os.path.join(INDEX_DIR, 'inverted_index.pkl'),
    'bm25_k1': 1.5,  # BM25 parameter (term frequency saturation)
    'bm25_b': 0.75,  # BM25 parameter (length normalization)
    'min_word_length': 3,  # Minimum word length to index
    'stop_words': True,  # Use stop words filtering
}

# Ranker settings (Abhiram's component)
RANKER_CONFIG = {
    'text_weight': 0.7,  # Weight for text relevance score
    'pagerank_weight': 0.3,  # Weight for PageRank score
    'top_k': 20,  # Number of top results to return
}

# Web interface settings
WEB_CONFIG = {
    'host': '0.0.0.0',
    'port': 5001,
    'debug': True,
}

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}