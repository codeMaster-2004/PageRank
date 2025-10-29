"""
Indexer and Text Processing Module
Team Member: Teja Nerella (nerella2@illinois.edu)
Responsibility: Build inverted index and implement BM25 scoring

This module processes text from crawled pages, builds an inverted
index, and implements BM25 ranking algorithm for text retrieval.
"""

import json
import pickle
import logging
import math
import re
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
from Backend.config import INDEXER_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BM25Indexer:
    """
    Inverted index with BM25 scoring for text retrieval
    """
    
    # Common English stop words
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
        'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
    }
    
    def __init__(self, k1: float = None, b: float = None, use_stop_words: bool = None):
        """
        Initialize BM25 indexer
        
        Args:
            k1: BM25 term frequency saturation parameter (default: 1.5)
            b: BM25 length normalization parameter (default: 0.75)
            use_stop_words: Whether to filter stop words (default: True)
        """
        self.k1 = k1 or INDEXER_CONFIG['bm25_k1']
        self.b = b or INDEXER_CONFIG['bm25_b']
        self.use_stop_words = use_stop_words if use_stop_words is not None else INDEXER_CONFIG['stop_words']
        
        # Index structures
        self.inverted_index = defaultdict(list)  # term -> [(doc_id, term_freq), ...]
        self.doc_lengths = {}  # doc_id -> document length
        self.doc_titles = {}  # doc_id -> document title (for retrieval)
        self.doc_count = 0
        self.avg_doc_length = 0.0
        self.idf_cache = {}  # Cache IDF values
        
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text: lowercase, remove punctuation, tokenize
        
        Args:
            text: Raw text string
            
        Returns:
            List of processed tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Keep only alphanumeric characters and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Tokenize
        tokens = text.split()
        
        # Filter tokens
        tokens = [
            token for token in tokens
            if len(token) >= INDEXER_CONFIG['min_word_length']
            and (not self.use_stop_words or token not in self.STOP_WORDS)
        ]
        
        return tokens
    
    def build_index(self, pages_data: Dict[str, Dict]):
        """
        Build inverted index from crawled pages
        
        Args:
            pages_data: Dictionary of page_title -> page_data
        """
        logger.info(f"Building index for {len(pages_data)} documents...")
        
        self.doc_count = len(pages_data)
        total_length = 0
        
        for doc_id, (page_title, page_data) in enumerate(pages_data.items()):
            # Store document title for retrieval
            self.doc_titles[doc_id] = page_title
            
            # Combine title, summary, and text for indexing
            # Weight title more heavily by including it multiple times
            text = (
                f"{page_data['title']} " * 3 +  # Title appears 3 times
                f"{page_data['summary']} " +
                page_data['text']
            )
            
            # Preprocess and tokenize
            tokens = self.preprocess_text(text)
            
            # Calculate term frequencies
            term_freq = Counter(tokens)
            
            # Store document length
            self.doc_lengths[doc_id] = len(tokens)
            total_length += len(tokens)
            
            # Add to inverted index
            for term, freq in term_freq.items():
                self.inverted_index[term].append((doc_id, freq))
            
            # Log progress
            if (doc_id + 1) % 500 == 0:
                logger.info(f"Indexed {doc_id + 1} documents...")
        
        # Calculate average document length
        self.avg_doc_length = total_length / self.doc_count if self.doc_count > 0 else 0
        
        logger.info(f"Index built successfully!")
        logger.info(f"Total terms: {len(self.inverted_index)}")
        logger.info(f"Average document length: {self.avg_doc_length:.2f}")
    
    def _calculate_idf(self, term: str) -> float:
        """
        Calculate IDF (Inverse Document Frequency) for a term
        
        Args:
            term: The term to calculate IDF for
            
        Returns:
            IDF value
        """
        if term in self.idf_cache:
            return self.idf_cache[term]
        
        # Number of documents containing the term
        df = len(self.inverted_index.get(term, []))
        
        # IDF formula: log((N - df + 0.5) / (df + 0.5) + 1)
        # Adding 1 to avoid negative IDF values
        idf = math.log((self.doc_count - df + 0.5) / (df + 0.5) + 1.0)
        
        self.idf_cache[term] = idf
        return idf
    
    def _calculate_bm25_score(self, term: str, doc_id: int, term_freq: int) -> float:
        """
        Calculate BM25 score for a term in a document
        
        Args:
            term: Query term
            doc_id: Document ID
            term_freq: Frequency of term in document
            
        Returns:
            BM25 score
        """
        # Get IDF
        idf = self._calculate_idf(term)
        
        # Get document length
        doc_length = self.doc_lengths[doc_id]
        
        # Calculate BM25 score
        # Formula: IDF * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / avgdl)))
        numerator = term_freq * (self.k1 + 1)
        denominator = term_freq + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
        
        score = idf * (numerator / denominator)
        return score
    
    def search(self, query: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """
        Search for documents matching the query using BM25
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of (page_title, bm25_score) tuples, sorted by score
        """
        # Preprocess query
        query_terms = self.preprocess_text(query)
        
        if not query_terms:
            logger.warning("Query has no valid terms after preprocessing")
            return []
        
        # Calculate BM25 scores for all documents
        doc_scores = defaultdict(float)
        
        for term in query_terms:
            if term not in self.inverted_index:
                continue
            
            # Get all documents containing this term
            for doc_id, term_freq in self.inverted_index[term]:
                score = self._calculate_bm25_score(term, doc_id, term_freq)
                doc_scores[doc_id] += score
        
        # Sort by score and return top-k
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        # Convert doc_id to page title
        results = [(self.doc_titles[doc_id], score) for doc_id, score in sorted_docs]
        
        return results
    
    def get_normalized_score(self, query: str, page_title: str) -> float:
        """
        Get normalized BM25 score (0-1 range) for a specific page
        
        Args:
            query: Search query
            page_title: Page title
            
        Returns:
            Normalized score
        """
        results = self.search(query, top_k=1000)  # Get many results for normalization
        
        if not results:
            return 0.0
        
        # Find the page in results
        page_score = 0.0
        for title, score in results:
            if title == page_title:
                page_score = score
                break
        
        # Normalize to 0-1 range
        max_score = results[0][1] if results else 0.0
        min_score = results[-1][1] if results else 0.0
        
        if max_score == min_score:
            return 1.0 if page_score > 0 else 0.0
        
        return (page_score - min_score) / (max_score - min_score)
    
    def save(self, index_file: str = None):
        """
        Save index to pickle file
        
        Args:
            index_file: Path to save index
        """
        index_file = index_file or INDEXER_CONFIG['index_file']
        
        data = {
            'inverted_index': dict(self.inverted_index),
            'doc_lengths': self.doc_lengths,
            'doc_titles': self.doc_titles,
            'doc_count': self.doc_count,
            'avg_doc_length': self.avg_doc_length,
            'k1': self.k1,
            'b': self.b,
        }
        
        with open(index_file, 'wb') as f:
            pickle.dump(data, f)
        
        logger.info(f"Saved index to {index_file}")
    
    @staticmethod
    def load(index_file: str = None) -> 'BM25Indexer':
        """
        Load index from pickle file
        
        Args:
            index_file: Path to index file
            
        Returns:
            BM25Indexer object with loaded index
        """
        index_file = index_file or INDEXER_CONFIG['index_file']
        
        with open(index_file, 'rb') as f:
            data = pickle.load(f)
        
        indexer = BM25Indexer(k1=data['k1'], b=data['b'])
        indexer.inverted_index = defaultdict(list, data['inverted_index'])
        indexer.doc_lengths = data['doc_lengths']
        indexer.doc_titles = data['doc_titles']
        indexer.doc_count = data['doc_count']
        indexer.avg_doc_length = data['avg_doc_length']
        
        logger.info(f"Loaded index with {len(indexer.inverted_index)} terms")
        return indexer