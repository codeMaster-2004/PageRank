"""
Ranking and Query Engine Module
Team Member: Abhiram Annaluru (abhia2@illinois.edu)
Responsibility: Combine PageRank and text relevance scores

This module implements the final ranking system that merges
PageRank scores with BM25 text relevance scores to produce
the best search results for user queries.
"""

import logging
from typing import List, Tuple, Dict
from config import RANKER_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchRanker:
    """
    Combined ranking engine using PageRank + BM25
    """
    
    def __init__(self, pagerank, indexer, text_weight: float = None, pagerank_weight: float = None):
        """
        Initialize the ranker
        
        Args:
            pagerank: PageRank object with computed scores
            indexer: BM25Indexer object with inverted index
            text_weight: Weight for text relevance (default: 0.7)
            pagerank_weight: Weight for PageRank score (default: 0.3)
        """
        self.pagerank = pagerank
        self.indexer = indexer
        self.text_weight = text_weight or RANKER_CONFIG['text_weight']
        self.pagerank_weight = pagerank_weight or RANKER_CONFIG['pagerank_weight']
        
        # Validate weights sum to 1
        if abs(self.text_weight + self.pagerank_weight - 1.0) > 1e-6:
            logger.warning(f"Weights don't sum to 1.0: {self.text_weight} + {self.pagerank_weight}")
            # Normalize weights
            total = self.text_weight + self.pagerank_weight
            self.text_weight /= total
            self.pagerank_weight /= total
        
        logger.info(f"Ranker initialized with weights: text={self.text_weight}, pagerank={self.pagerank_weight}")
    
    def search(self, query: str, top_k: int = None, return_details: bool = False) -> List[Tuple]:
        """
        Search and rank documents using combined scoring
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            return_details: If True, return detailed scores
            
        Returns:
            List of results. Each result is either:
            - (page_title, combined_score) if return_details=False
            - (page_title, combined_score, text_score, pr_score) if return_details=True
        """
        top_k = top_k or RANKER_CONFIG['top_k']
        
        logger.info(f"Searching for: '{query}'")
        
        # Get BM25 results (get more than top_k for better PageRank integration)
        bm25_results = self.indexer.search(query, top_k=top_k * 5)
        
        if not bm25_results:
            logger.warning("No BM25 results found")
            return []
        
        # Normalize BM25 scores to 0-1 range
        bm25_scores = {title: score for title, score in bm25_results}
        max_bm25 = max(bm25_scores.values())
        min_bm25 = min(bm25_scores.values())
        
        if max_bm25 == min_bm25:
            normalized_bm25 = {title: 1.0 for title in bm25_scores}
        else:
            normalized_bm25 = {
                title: (score - min_bm25) / (max_bm25 - min_bm25)
                for title, score in bm25_scores.items()
            }
        
        # Combine with PageRank scores
        combined_scores = []
        
        for page_title in bm25_scores.keys():
            # Get normalized scores
            text_score = normalized_bm25[page_title]
            pr_score = self.pagerank.get_normalized_score(page_title)
            
            # Combined score: weighted sum
            combined_score = (
                self.text_weight * text_score +
                self.pagerank_weight * pr_score
            )
            
            if return_details:
                combined_scores.append((page_title, combined_score, text_score, pr_score))
            else:
                combined_scores.append((page_title, combined_score))
        
        # Sort by combined score and return top-k
        combined_scores.sort(key=lambda x: x[1], reverse=True)
        results = combined_scores[:top_k]
        
        logger.info(f"Returning {len(results)} results")
        
        return results
    
    def compare_rankings(self, query: str, top_k: int = 10):
        """
        Compare rankings with and without PageRank integration
        Useful for evaluation and debugging
        
        Args:
            query: Search query
            top_k: Number of results to compare
        """
        print(f"\n{'='*80}")
        print(f"QUERY: '{query}'")
        print(f"{'='*80}\n")
        
        # BM25 only results
        bm25_results = self.indexer.search(query, top_k=top_k)
        
        # Combined results with details
        combined_results = self.search(query, top_k=top_k, return_details=True)
        
        # Print side by side
        print(f"{'BM25 ONLY':<50} | {'COMBINED (BM25 + PageRank)':<50}")
        print(f"{'-'*50} | {'-'*50}")
        
        for i in range(max(len(bm25_results), len(combined_results))):
            # BM25 side
            if i < len(bm25_results):
                bm25_title, bm25_score = bm25_results[i]
                bm25_str = f"{i+1}. {bm25_title[:40]:<40} ({bm25_score:.3f})"
            else:
                bm25_str = " " * 50
            
            # Combined side
            if i < len(combined_results):
                title, combined, text, pr = combined_results[i]
                combined_str = f"{i+1}. {title[:30]:<30} [C:{combined:.3f} T:{text:.3f} P:{pr:.3f}]"
            else:
                combined_str = ""
            
            print(f"{bm25_str} | {combined_str}")
        
        print(f"\n{'='*80}\n")
    
    def batch_search(self, queries: List[str], top_k: int = None) -> Dict[str, List[Tuple]]:
        """
        Perform batch search for multiple queries
        
        Args:
            queries: List of query strings
            top_k: Number of results per query
            
        Returns:
            Dictionary mapping query -> results
        """
        results = {}
        
        for query in queries:
            results[query] = self.search(query, top_k=top_k)
        
        return results


def main():
    """
    Example usage of the ranker
    """
    from crawler import WikipediaCrawler
    from pagerank import PageRank
    from indexer import BM25Indexer
    
    # Load data
    try:
        logger.info("Loading data...")
        pages_data, link_graph = WikipediaCrawler.load_data()
        pagerank = PageRank.load()
        indexer = BM25Indexer.load()
    except FileNotFoundError as e:
        logger.error(f"Required data not found: {e}")
        logger.error("Please run crawler.py, pagerank.py, and indexer.py first!")
        return
    
    # Create ranker
    ranker = SearchRanker(pagerank, indexer)
    
    # Test queries
    test_queries = [
        'machine learning',
        'artificial intelligence',
        'graph algorithms',
        'neural networks',
        'deep learning',
    ]
    
    print("\n=== Search Results with Combined Ranking ===\n")
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 80)
        
        results = ranker.search(query, top_k=5, return_details=True)
        
        for i, (title, combined, text, pr) in enumerate(results, 1):
            print(f"{i}. {title}")
            print(f"   Combined: {combined:.4f} | Text: {text:.4f} | PageRank: {pr:.4f}")
    
    # Show comparison for one query
    print("\n" + "="*80)
    print("COMPARISON: BM25 vs Combined Ranking")
    print("="*80)
    ranker.compare_rankings('machine learning', top_k=10)


if __name__ == "__main__":
    main()