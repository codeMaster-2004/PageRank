"""
PageRank Algorithm Module
Team Member: Kundan Mergu (kmerg2@illinois.edu)
Responsibility: Implement PageRank algorithm with convergence guarantees

This module computes PageRank scores for web pages based on their
link structure. It uses the power iteration method with a damping
factor of 0.85 and convergence threshold of 1e-6.
"""

import json
import pickle
import logging
import numpy as np
from typing import Dict, List
from Backend.config import PAGERANK_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PageRank:
    """
    PageRank computation using power iteration method
    """
    
    def __init__(self, damping_factor: float = None, threshold: float = None, max_iterations: int = None):
        """
        Initialize PageRank computer
        
        Args:
            damping_factor: Probability of following a link (default: 0.85)
            threshold: L1 norm convergence threshold (default: 1e-6)
            max_iterations: Maximum iterations before stopping (default: 100)
        """
        self.damping_factor = damping_factor or PAGERANK_CONFIG['damping_factor']
        self.threshold = threshold or PAGERANK_CONFIG['convergence_threshold']
        self.max_iterations = max_iterations or PAGERANK_CONFIG['max_iterations']
        
        self.pagerank_scores = {}
        self.iterations_to_converge = 0
        
    def compute(self, link_graph: Dict[str, List[str]]) -> Dict[str, float]:
        """
        Compute PageRank scores for all pages in the graph
        
        Args:
            link_graph: Dictionary mapping page -> list of outgoing links
            
        Returns:
            Dictionary mapping page -> PageRank score
        """
        logger.info("Starting PageRank computation...")
        logger.info(f"Graph size: {len(link_graph)} nodes")
        
        # Get all unique pages (nodes)
        all_pages = set(link_graph.keys())
        for links in link_graph.values():
            all_pages.update(links)
        
        pages_list = sorted(list(all_pages))
        n_pages = len(pages_list)
        page_to_idx = {page: idx for idx, page in enumerate(pages_list)}
        
        logger.info(f"Total unique pages: {n_pages}")
        
        # Build adjacency matrix (incoming links)
        # incoming_links[i] = list of pages that link to page i
        incoming_links = {i: [] for i in range(n_pages)}
        outgoing_counts = {i: 0 for i in range(n_pages)}
        
        for source_page, target_pages in link_graph.items():
            if source_page not in page_to_idx:
                continue
            source_idx = page_to_idx[source_page]
            outgoing_counts[source_idx] = len(target_pages)
            
            for target_page in target_pages:
                if target_page in page_to_idx:
                    target_idx = page_to_idx[target_page]
                    incoming_links[target_idx].append(source_idx)
        
        # Initialize PageRank scores (uniform distribution)
        pagerank = np.ones(n_pages) / n_pages
        
        # Power iteration
        for iteration in range(self.max_iterations):
            new_pagerank = np.zeros(n_pages)
            
            # Random surfer component
            random_component = (1 - self.damping_factor) / n_pages
            
            # Link following component
            for i in range(n_pages):
                link_component = 0.0
                for source_idx in incoming_links[i]:
                    if outgoing_counts[source_idx] > 0:
                        link_component += pagerank[source_idx] / outgoing_counts[source_idx]
                
                new_pagerank[i] = random_component + self.damping_factor * link_component
            
            # Normalize to ensure sum = 1
            new_pagerank /= new_pagerank.sum()
            
            # Check convergence (L1 norm)
            diff = np.abs(new_pagerank - pagerank).sum()
            
            if diff < self.threshold:
                logger.info(f"Converged after {iteration + 1} iterations (diff: {diff:.2e})")
                self.iterations_to_converge = iteration + 1
                pagerank = new_pagerank
                break
            
            pagerank = new_pagerank
            
            # Log progress every 10 iterations
            if (iteration + 1) % 10 == 0:
                logger.info(f"Iteration {iteration + 1}: L1 diff = {diff:.2e}")
        
        else:
            logger.warning(f"Did not converge after {self.max_iterations} iterations")
            self.iterations_to_converge = self.max_iterations
        
        # Convert back to dictionary
        self.pagerank_scores = {
            pages_list[i]: float(pagerank[i]) 
            for i in range(n_pages)
        }
        
        # Log top pages
        top_pages = sorted(self.pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        logger.info("\nTop 10 pages by PageRank:")
        for page, score in top_pages:
            logger.info(f"  {page}: {score:.6f}")
        
        return self.pagerank_scores
    
    def save(self, pickle_file: str = None, json_file: str = None):
        """
        Save PageRank scores to files
        
        Args:
            pickle_file: Path to save pickle file (fast loading)
            json_file: Path to save JSON file (portable)
        """
        pickle_file = pickle_file or PAGERANK_CONFIG['output_file']
        json_file = json_file or PAGERANK_CONFIG['output_json']
        
        # Save as pickle (for Python use)
        with open(pickle_file, 'wb') as f:
            pickle.dump({
                'scores': self.pagerank_scores,
                'iterations': self.iterations_to_converge,
                'damping_factor': self.damping_factor,
            }, f)
        logger.info(f"Saved PageRank scores to {pickle_file}")
        
        # Save as JSON (for portability)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'scores': self.pagerank_scores,
                'iterations': self.iterations_to_converge,
                'damping_factor': self.damping_factor,
            }, f, indent=2)
        logger.info(f"Saved PageRank scores to {json_file}")
    
    @staticmethod
    def load(pickle_file: str = None) -> 'PageRank':
        """
        Load previously computed PageRank scores
        
        Args:
            pickle_file: Path to pickle file
            
        Returns:
            PageRank object with loaded scores
        """
        pickle_file = pickle_file or PAGERANK_CONFIG['output_file']
        
        with open(pickle_file, 'rb') as f:
            data = pickle.load(f)
        
        pr = PageRank(damping_factor=data['damping_factor'])
        pr.pagerank_scores = data['scores']
        pr.iterations_to_converge = data['iterations']
        
        logger.info(f"Loaded PageRank scores for {len(pr.pagerank_scores)} pages")
        return pr
    
    def get_score(self, page: str) -> float:
        """
        Get PageRank score for a specific page
        
        Args:
            page: Page title
            
        Returns:
            PageRank score (or 0 if page not found)
        """
        return self.pagerank_scores.get(page, 0.0)
    
    def get_normalized_score(self, page: str) -> float:
        """
        Get normalized PageRank score (0-1 range)
        
        Args:
            page: Page title
            
        Returns:
            Normalized score
        """
        if not self.pagerank_scores:
            return 0.0
        
        score = self.get_score(page)
        max_score = max(self.pagerank_scores.values())
        min_score = min(self.pagerank_scores.values())
        
        if max_score == min_score:
            return 0.5
        
        return (score - min_score) / (max_score - min_score)