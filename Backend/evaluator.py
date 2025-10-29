"""
Evaluation and Experimentation Module
Team Member: Kundan Mergu (kmerg2@illinois.edu)
Responsibility: Evaluate retrieval quality and system performance

This module implements evaluation metrics (Precision, Recall, NDCG)
and analyzes the effectiveness of PageRank integration in the search system.
"""

import json
import time
import logging
import numpy as np
from typing import List, Dict, Tuple, Set
from collections import defaultdict
from Backend.config import EVALUATOR_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchEvaluator:
    """
    Evaluation framework for search quality and system performance
    """
    
    def __init__(self, ranker):
        """
        Initialize evaluator
        
        Args:
            ranker: SearchRanker object to evaluate
        """
        self.ranker = ranker
        self.relevance_judgments = {}  # query -> {page: relevance_score}
        self.evaluation_results = {}
        
    def load_relevance_judgments(self, filepath: str = None):
        """
        Load manual relevance judgments from file
        
        Args:
            filepath: Path to relevance judgments JSON file
        """
        filepath = filepath or EVALUATOR_CONFIG['relevance_file']
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.relevance_judgments = json.load(f)
            logger.info(f"Loaded relevance judgments for {len(self.relevance_judgments)} queries")
        except FileNotFoundError:
            logger.warning(f"No relevance judgments found at {filepath}")
            logger.info("You can create relevance judgments using create_relevance_template()")
    
    def save_relevance_judgments(self, filepath: str = None):
        """
        Save relevance judgments to file
        
        Args:
            filepath: Path to save relevance judgments
        """
        filepath = filepath or EVALUATOR_CONFIG['relevance_file']
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.relevance_judgments, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved relevance judgments to {filepath}")
    
    def create_relevance_template(self, queries: List[str] = None, top_k: int = 20):
        """
        Create a template for manual relevance judgments
        
        Args:
            queries: List of queries to evaluate
            top_k: Number of results to judge per query
        """
        queries = queries or EVALUATOR_CONFIG['test_queries']
        
        template = {}
        
        for query in queries:
            results = self.ranker.search(query, top_k=top_k)
            
            # Create template with placeholder relevance scores
            template[query] = {
                page_title: 0  # 0 = not relevant, 1 = somewhat relevant, 2 = highly relevant
                for page_title, _ in results
            }
        
        return template
    
    def calculate_precision(self, retrieved: List[str], relevant: Set[str]) -> float:
        """
        Calculate precision: relevant results / retrieved results
        
        Args:
            retrieved: List of retrieved page titles
            relevant: Set of relevant page titles
            
        Returns:
            Precision score (0-1)
        """
        if not retrieved:
            return 0.0
        
        relevant_retrieved = sum(1 for page in retrieved if page in relevant)
        return relevant_retrieved / len(retrieved)
    
    def calculate_recall(self, retrieved: List[str], relevant: Set[str]) -> float:
        """
        Calculate recall: relevant results retrieved / total relevant
        
        Args:
            retrieved: List of retrieved page titles
            relevant: Set of relevant page titles
            
        Returns:
            Recall score (0-1)
        """
        if not relevant:
            return 0.0
        
        relevant_retrieved = sum(1 for page in retrieved if page in relevant)
        return relevant_retrieved / len(relevant)
    
    def calculate_f1(self, precision: float, recall: float) -> float:
        """
        Calculate F1 score: harmonic mean of precision and recall
        
        Args:
            precision: Precision score
            recall: Recall score
            
        Returns:
            F1 score
        """
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def calculate_ndcg(self, retrieved: List[str], relevance_scores: Dict[str, int], k: int = None) -> float:
        """
        Calculate NDCG@k (Normalized Discounted Cumulative Gain)
        
        Args:
            retrieved: List of retrieved page titles (in rank order)
            relevance_scores: Dictionary of page -> relevance score
            k: Calculate NDCG@k (default: length of retrieved)
            
        Returns:
            NDCG score (0-1)
        """
        k = k or len(retrieved)
        retrieved_k = retrieved[:k]
        
        # Calculate DCG (Discounted Cumulative Gain)
        dcg = 0.0
        for i, page in enumerate(retrieved_k, 1):
            relevance = relevance_scores.get(page, 0)
            dcg += (2**relevance - 1) / np.log2(i + 1)
        
        # Calculate IDCG (Ideal DCG)
        ideal_relevances = sorted(relevance_scores.values(), reverse=True)[:k]
        idcg = 0.0
        for i, relevance in enumerate(ideal_relevances, 1):
            idcg += (2**relevance - 1) / np.log2(i + 1)
        
        # NDCG = DCG / IDCG
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    def evaluate_query(self, query: str, k: int = 10) -> Dict[str, float]:
        """
        Evaluate search results for a single query
        
        Args:
            query: Search query
            k: Evaluate top-k results
            
        Returns:
            Dictionary of metrics
        """
        if query not in self.relevance_judgments:
            logger.warning(f"No relevance judgments for query: '{query}'")
            return {}
        
        # Get search results
        results = self.ranker.search(query, top_k=k)
        retrieved = [page_title for page_title, _ in results]
        
        # Get relevant pages (those with relevance score > 0)
        relevance_scores = self.relevance_judgments[query]
        relevant = {page for page, score in relevance_scores.items() if score > 0}
        
        # Calculate metrics
        precision = self.calculate_precision(retrieved, relevant)
        recall = self.calculate_recall(retrieved, relevant)
        f1 = self.calculate_f1(precision, recall)
        ndcg = self.calculate_ndcg(retrieved, relevance_scores, k=k)
        
        metrics = {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'ndcg': ndcg,
        }
        
        return metrics
    
    def evaluate_all(self, queries: List[str] = None, k: int = None) -> Dict[str, Dict]:
        """
        Evaluate all queries and compute aggregate metrics
        
        Args:
            queries: List of queries to evaluate (default: all with judgments)
            k: Evaluate top-k results
            
        Returns:
            Dictionary with per-query and aggregate metrics
        """
        k = k or EVALUATOR_CONFIG['ndcg_k']
        
        if queries is None:
            queries = list(self.relevance_judgments.keys())
        
        logger.info(f"Evaluating {len(queries)} queries...")
        
        results = {}
        all_metrics = defaultdict(list)
        
        for query in queries:
            metrics = self.evaluate_query(query, k=k)
            
            if metrics:
                results[query] = metrics
                
                # Collect for aggregation
                for metric_name, value in metrics.items():
                    all_metrics[metric_name].append(value)
        
        # Calculate aggregate metrics (mean)
        aggregate = {
            metric_name: np.mean(values)
            for metric_name, values in all_metrics.items()
        }
        
        self.evaluation_results = {
            'per_query': results,
            'aggregate': aggregate,
            'k': k,
        }
        
        return self.evaluation_results
    
    def compare_with_without_pagerank(self, queries: List[str] = None, k: int = 10):
        """
        Compare search results with and without PageRank integration
        
        Args:
            queries: List of queries to compare
            k: Compare top-k results
        """
        queries = queries or EVALUATOR_CONFIG['test_queries'][:5]
        
        print(f"\n{'='*100}")
        print("COMPARISON: With PageRank vs Without PageRank (BM25 only)")
        print(f"{'='*100}\n")
        
        # Save original weights
        original_text_weight = self.ranker.text_weight
        original_pr_weight = self.ranker.pagerank_weight
        
        for query in queries:
            print(f"Query: '{query}'")
            print("-" * 100)
            
            # With PageRank
            self.ranker.text_weight = original_text_weight
            self.ranker.pagerank_weight = original_pr_weight
            with_pr = self.ranker.search(query, top_k=k, return_details=True)
            
            # Without PageRank (text only)
            self.ranker.text_weight = 1.0
            self.ranker.pagerank_weight = 0.0
            without_pr = self.ranker.search(query, top_k=k, return_details=True)
            
            # Restore weights
            self.ranker.text_weight = original_text_weight
            self.ranker.pagerank_weight = original_pr_weight
            
            # Print comparison
            print(f"{'WITH PageRank':<48} | {'WITHOUT PageRank (BM25 only)':<48}")
            print(f"{'-'*48} | {'-'*48}")
            
            for i in range(k):
                if i < len(with_pr):
                    title_w, score_w, _, pr = with_pr[i]
                    with_str = f"{i+1}. {title_w[:35]:<35} ({score_w:.3f})"
                else:
                    with_str = " " * 48
                
                if i < len(without_pr):
                    title_wo, score_wo, _, _ = without_pr[i]
                    without_str = f"{i+1}. {title_wo[:35]:<35} ({score_wo:.3f})"
                else:
                    without_str = ""
                
                print(f"{with_str} | {without_str}")
            
            print()
    
    def measure_performance(self, queries: List[str] = None, iterations: int = 5) -> Dict[str, float]:
        """
        Measure system performance (query response time)
        
        Args:
            queries: List of queries to test
            iterations: Number of iterations per query
            
        Returns:
            Dictionary of performance metrics
        """
        queries = queries or EVALUATOR_CONFIG['test_queries']
        
        logger.info(f"Measuring performance over {len(queries)} queries, {iterations} iterations each")
        
        response_times = []
        
        for query in queries:
            for _ in range(iterations):
                start_time = time.time()
                self.ranker.search(query, top_k=20)
                end_time = time.time()
                
                response_times.append(end_time - start_time)
        
        performance = {
            'mean_response_time': np.mean(response_times),
            'median_response_time': np.median(response_times),
            'min_response_time': np.min(response_times),
            'max_response_time': np.max(response_times),
            'std_response_time': np.std(response_times),
        }
        
        return performance
    
    def print_evaluation_report(self):
        """
        Print a comprehensive evaluation report
        """
        if not self.evaluation_results:
            logger.error("No evaluation results. Run evaluate_all() first!")
            return
        
        print(f"\n{'='*80}")
        print("EVALUATION REPORT")
        print(f"{'='*80}\n")
        
        # Aggregate metrics
        aggregate = self.evaluation_results['aggregate']
        k = self.evaluation_results['k']
        
        print(f"Aggregate Metrics (averaged over {len(self.evaluation_results['per_query'])} queries)")
        print("-" * 80)
        print(f"Precision@{k}:  {aggregate['precision']:.4f}")
        print(f"Recall@{k}:     {aggregate['recall']:.4f}")
        print(f"F1@{k}:         {aggregate['f1']:.4f}")
        print(f"NDCG@{k}:       {aggregate['ndcg']:.4f}")
        
        # Per-query metrics
        print(f"\n\nPer-Query Metrics")
        print("-" * 80)
        print(f"{'Query':<35} | {'Precision':<10} | {'Recall':<10} | {'F1':<10} | {'NDCG':<10}")
        print("-" * 80)
        
        for query, metrics in self.evaluation_results['per_query'].items():
            print(f"{query[:35]:<35} | {metrics['precision']:<10.4f} | {metrics['recall']:<10.4f} | "
                  f"{metrics['f1']:<10.4f} | {metrics['ndcg']:<10.4f}")
        
        print(f"\n{'='*80}\n")