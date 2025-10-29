"""
Data Analysis and Statistics Module
Analyze crawled data, link structure, and PageRank scores

Usage:
    python analyze_data.py                    # Show all statistics
    python analyze_data.py --graph           # Show graph statistics only
    python analyze_data.py --pagerank        # Show PageRank statistics only
    python analyze_data.py --top 20          # Show top 20 pages
"""

import json
import argparse
import logging
import numpy as np
from collections import Counter, defaultdict
from crawler import WikipediaCrawler
from pagerank import PageRank

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataAnalyzer:
    """
    Analyze crawled data and compute statistics
    """
    
    def __init__(self):
        self.pages_data = None
        self.link_graph = None
        self.pagerank = None
        
    def load_data(self):
        """
        Load all available data
        """
        try:
            self.pages_data, self.link_graph = WikipediaCrawler.load_data()
            logger.info(f"Loaded {len(self.pages_data)} pages")
        except FileNotFoundError:
            logger.warning("No crawled data found. Run crawler.py first!")
            
        try:
            self.pagerank = PageRank.load()
            logger.info(f"Loaded PageRank scores for {len(self.pagerank.pagerank_scores)} pages")
        except FileNotFoundError:
            logger.warning("No PageRank data found. Run pagerank.py first!")
    
    def analyze_basic_stats(self):
        """
        Show basic statistics about crawled data
        """
        if not self.pages_data:
            return
        
        print("\n" + "="*80)
        print("BASIC STATISTICS")
        print("="*80)
        
        # Page count
        print(f"\nTotal pages crawled: {len(self.pages_data)}")
        
        # Text statistics
        text_lengths = [len(page['text']) for page in self.pages_data.values()]
        print(f"\nText length statistics:")
        print(f"  Mean: {np.mean(text_lengths):.0f} characters")
        print(f"  Median: {np.median(text_lengths):.0f} characters")
        print(f"  Min: {np.min(text_lengths)} characters")
        print(f"  Max: {np.max(text_lengths)} characters")
        
        # Summary lengths
        summary_lengths = [len(page['summary']) for page in self.pages_data.values()]
        print(f"\nSummary length statistics:")
        print(f"  Mean: {np.mean(summary_lengths):.0f} characters")
        print(f"  Median: {np.median(summary_lengths):.0f} characters")
        
        # Category statistics
        all_categories = []
        for page in self.pages_data.values():
            all_categories.extend(page.get('categories', []))
        
        category_counts = Counter(all_categories)
        print(f"\nTotal unique categories: {len(category_counts)}")
        print(f"Top 10 categories:")
        for category, count in category_counts.most_common(10):
            print(f"  {category}: {count} pages")
    
    def analyze_graph_structure(self):
        """
        Analyze link graph structure
        """
        if not self.link_graph:
            return
        
        print("\n" + "="*80)
        print("GRAPH STRUCTURE ANALYSIS")
        print("="*80)
        
        # Total links
        total_links = sum(len(links) for links in self.link_graph.values())
        print(f"\nTotal links: {total_links}")
        print(f"Total nodes: {len(self.link_graph)}")
        
        # Degree distribution
        out_degrees = [len(links) for links in self.link_graph.values()]
        in_degrees = defaultdict(int)
        for source, targets in self.link_graph.items():
            for target in targets:
                in_degrees[target] += 1
        
        in_degree_values = list(in_degrees.values())
        
        print(f"\nOut-degree statistics (outgoing links):")
        print(f"  Mean: {np.mean(out_degrees):.2f}")
        print(f"  Median: {np.median(out_degrees):.0f}")
        print(f"  Max: {np.max(out_degrees)}")
        print(f"  Min: {np.min(out_degrees)}")
        
        print(f"\nIn-degree statistics (incoming links):")
        print(f"  Mean: {np.mean(in_degree_values):.2f}")
        print(f"  Median: {np.median(in_degree_values):.0f}")
        print(f"  Max: {np.max(in_degree_values)}")
        print(f"  Min: {np.min(in_degree_values)}")
        
        # Most linked pages (by in-degree)
        print(f"\nTop 15 pages by incoming links:")
        sorted_in_degrees = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)
        for i, (page, degree) in enumerate(sorted_in_degrees[:15], 1):
            print(f"  {i:2d}. {page[:60]:<60} ({degree} incoming links)")
        
        # Dangling nodes (no outgoing links)
        dangling = [page for page, links in self.link_graph.items() if len(links) == 0]
        print(f"\nDangling nodes (no outgoing links): {len(dangling)}")
        
        # Isolated nodes (no incoming or outgoing links)
        isolated = [page for page in dangling if page not in in_degrees]
        print(f"Isolated nodes (no links at all): {len(isolated)}")
        
        # Graph density
        max_possible_edges = len(self.link_graph) * (len(self.link_graph) - 1)
        density = total_links / max_possible_edges if max_possible_edges > 0 else 0
        print(f"\nGraph density: {density:.6f} ({density*100:.4f}%)")
    
    def analyze_pagerank_scores(self, top_k=20):
        """
        Analyze PageRank score distribution
        
        Args:
            top_k: Number of top pages to show
        """
        if not self.pagerank:
            return
        
        print("\n" + "="*80)
        print("PAGERANK SCORE ANALYSIS")
        print("="*80)
        
        scores = list(self.pagerank.pagerank_scores.values())
        
        print(f"\nPageRank score statistics:")
        print(f"  Mean: {np.mean(scores):.6f}")
        print(f"  Median: {np.median(scores):.6f}")
        print(f"  Std Dev: {np.std(scores):.6f}")
        print(f"  Min: {np.min(scores):.6f}")
        print(f"  Max: {np.max(scores):.6f}")
        
        print(f"\nConvergence information:")
        print(f"  Iterations: {self.pagerank.iterations_to_converge}")
        print(f"  Damping factor: {self.pagerank.damping_factor}")
        
        # Top pages by PageRank
        print(f"\nTop {top_k} pages by PageRank score:")
        sorted_pages = sorted(
            self.pagerank.pagerank_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        for i, (page, score) in enumerate(sorted_pages[:top_k], 1):
            # Get in-degree if available
            in_degree = 0
            if self.link_graph:
                for targets in self.link_graph.values():
                    if page in targets:
                        in_degree += 1
            
            print(f"  {i:2d}. {page[:55]:<55} "
                  f"PR: {score:.6f}  Links: {in_degree:4d}")
        
        # Score distribution
        print(f"\nPageRank score distribution:")
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        for p in percentiles:
            value = np.percentile(scores, p)
            print(f"  {p:2d}th percentile: {value:.6f}")
    
    def compare_pagerank_with_indegree(self, top_k=20):
        """
        Compare PageRank scores with simple in-degree counts
        """
        if not self.pagerank or not self.link_graph:
            return
        
        print("\n" + "="*80)
        print("PAGERANK vs IN-DEGREE COMPARISON")
        print("="*80)
        
        # Calculate in-degrees
        in_degrees = defaultdict(int)
        for targets in self.link_graph.values():
            for target in targets:
                in_degrees[target] += 1
        
        # Get top pages by each metric
        top_by_pr = sorted(
            self.pagerank.pagerank_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        top_by_indegree = sorted(
            in_degrees.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        # Show comparison
        print(f"\n{'TOP BY PAGERANK':<60} | {'TOP BY IN-DEGREE':<60}")
        print("-"*60 + " | " + "-"*60)
        
        for i in range(top_k):
            # PageRank side
            if i < len(top_by_pr):
                pr_page, pr_score = top_by_pr[i]
                pr_indegree = in_degrees.get(pr_page, 0)
                pr_str = f"{i+1:2d}. {pr_page[:40]:<40} PR:{pr_score:.5f} In:{pr_indegree:3d}"
            else:
                pr_str = " " * 60
            
            # In-degree side
            if i < len(top_by_indegree):
                id_page, id_count = top_by_indegree[i]
                id_pr = self.pagerank.pagerank_scores.get(id_page, 0)
                id_str = f"{i+1:2d}. {id_page[:40]:<40} In:{id_count:3d} PR:{id_pr:.5f}"
            else:
                id_str = ""
            
            print(f"{pr_str} | {id_str}")
        
        # Calculate correlation
        common_pages = set(self.pagerank.pagerank_scores.keys()) & set(in_degrees.keys())
        if common_pages:
            pr_values = [self.pagerank.pagerank_scores[p] for p in common_pages]
            id_values = [in_degrees[p] for p in common_pages]
            correlation = np.corrcoef(pr_values, id_values)[0, 1]
            print(f"\nCorrelation between PageRank and In-Degree: {correlation:.4f}")
    
    def export_statistics(self, filename='results/data_statistics.json'):
        """
        Export all statistics to a JSON file
        """
        stats = {}
        
        if self.pages_data:
            text_lengths = [len(page['text']) for page in self.pages_data.values()]
            stats['pages'] = {
                'count': len(self.pages_data),
                'text_length_mean': float(np.mean(text_lengths)),
                'text_length_median': float(np.median(text_lengths)),
            }
        
        if self.link_graph:
            out_degrees = [len(links) for links in self.link_graph.values()]
            stats['graph'] = {
                'nodes': len(self.link_graph),
                'edges': sum(len(links) for links in self.link_graph.values()),
                'avg_out_degree': float(np.mean(out_degrees)),
            }
        
        if self.pagerank:
            scores = list(self.pagerank.pagerank_scores.values())
            stats['pagerank'] = {
                'iterations': self.pagerank.iterations_to_converge,
                'score_mean': float(np.mean(scores)),
                'score_median': float(np.median(scores)),
                'score_max': float(np.max(scores)),
            }
        
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n✓ Statistics exported to {filename}")


def main():
    """
    Main analysis function
    """
    parser = argparse.ArgumentParser(description='Analyze PageRank Search Engine Data')
    parser.add_argument('--graph', action='store_true', help='Show graph statistics only')
    parser.add_argument('--pagerank', action='store_true', help='Show PageRank statistics only')
    parser.add_argument('--top', type=int, default=20, help='Number of top pages to show')
    parser.add_argument('--export', action='store_true', help='Export statistics to JSON')
    
    args = parser.parse_args()
    
    # Create analyzer and load data
    analyzer = DataAnalyzer()
    analyzer.load_data()
    
    # Run analyses based on arguments
    if args.graph:
        analyzer.analyze_graph_structure()
    elif args.pagerank:
        analyzer.analyze_pagerank_scores(top_k=args.top)
    else:
        # Show all statistics
        analyzer.analyze_basic_stats()
        analyzer.analyze_graph_structure()
        analyzer.analyze_pagerank_scores(top_k=args.top)
        analyzer.compare_pagerank_with_indegree(top_k=15)
    
    # Export if requested
    if args.export:
        analyzer.export_statistics()


if __name__ == "__main__":
    main()