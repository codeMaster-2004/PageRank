"""
Main Orchestrator for PageRank Search Engine
Central entry point that coordinates all team components
Uses WikipediaCrawler for fast crawling with curated CS topics

Usage:
    python3 -m Backend.main --help                    # Show all options
    python3 -m Backend.main --full-pipeline           # Runs everything on this main file
    python3 -m Backend.main --crawl --max-pages 250   # Crawl 250 pages (recommended)
    python3 -m Backend.main --index                   # Only build index
    python3 -m Backend.main --search "query"          # Search
    python3 -m Backend.main --full-pipeline           # Run everything
    python3 -m Backend.main --serve                   # Start web server
"""
import argparse
import logging
import sys
import time
from typing import Optional

# Import all team member components
from Backend.web_crawler import WikipediaCrawler
from Backend.pagerank import PageRank
from Backend.indexer import BM25Indexer
from Backend.ranker import SearchRanker
from Backend.evaluator import SearchEvaluator
from Frontend.app import app, load_search_engine
import Backend.config as config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PageRankSearchEngine:
    """
    Main search engine class that coordinates all components
    """
    
    def __init__(self):
        """Initialize the search engine"""
        self.crawler = None
        self.pagerank = None
        self.indexer = None
        self.ranker = None
        self.evaluator = None
        
        self.pages_data = None
        self.link_graph = None
        
    def crawl_wikipedia(self, max_pages: Optional[int] = None) -> bool:
        """
        Step 1: Crawl Wikipedia pages (Gulnaaz's component)
        Uses WikipediaCrawler for faster crawling
        
        Args:
            max_pages: Maximum number of pages to crawl
            
        Returns:
            True if successful, False otherwise
        """
        logger.info("="*80)
        logger.info("STEP 1: CRAWLING WIKIPEDIA (Gulnaaz's Component)")
        logger.info("="*80)
        
        try:
            self.crawler = WikipediaCrawler(max_pages=max_pages)
            self.pages_data, self.link_graph = self.crawler.crawl()
            self.crawler.save_data()
            
            logger.info(f"✓ Successfully crawled {len(self.pages_data)} pages")
            return True
            
        except Exception as e:
            logger.error(f"✗ Crawling failed: {e}")
            return False
    
    def compute_pagerank(self) -> bool:
        """
        Step 2: Compute PageRank scores (Shikhar's component)
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 2: COMPUTING PAGERANK (Shikhar's Component)")
        logger.info("="*80)
        
        try:
            # Load data if not already loaded
            if self.link_graph is None:
                self.pages_data, self.link_graph = WikipediaCrawler.load_data()
            
            # Compute PageRank
            self.pagerank = PageRank()
            self.pagerank.compute(self.link_graph)
            self.pagerank.save()
            
            logger.info(f"✓ PageRank computed successfully")
            logger.info(f"  Converged in {self.pagerank.iterations_to_converge} iterations")
            return True
            
        except Exception as e:
            logger.error(f"✗ PageRank computation failed: {e}")
            return False
    
    def build_index(self) -> bool:
        """
        Step 3: Build search index (Teja's component)
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 3: BUILDING SEARCH INDEX (Teja's Component)")
        logger.info("="*80)
        
        try:
            # Load data if not already loaded
            if self.pages_data is None:
                self.pages_data, self.link_graph = WikipediaCrawler.load_data()
            
            # Build index
            self.indexer = BM25Indexer()
            self.indexer.build_index(self.pages_data)
            self.indexer.save()
            
            logger.info(f"✓ Index built successfully")
            logger.info(f"  Total terms: {len(self.indexer.inverted_index)}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Index building failed: {e}")
            return False
    
    def initialize_ranker(self) -> bool:
        """
        Step 4: Initialize ranking engine (Abhiram's component)
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 4: INITIALIZING RANKER (Abhiram's Component)")
        logger.info("="*80)
        
        try:
            # Load components if not already loaded
            if self.pagerank is None:
                self.pagerank = PageRank.load()
            
            if self.indexer is None:
                self.indexer = BM25Indexer.load()
            
            # Initialize ranker
            self.ranker = SearchRanker(self.pagerank, self.indexer)
            
            logger.info(f"✓ Ranker initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"✗ Ranker initialization failed: {e}")
            return False
    
    def search(self, query: str, top_k: int = 10, show_details: bool = True):
        """
        Perform a search query
        
        Args:
            query: Search query string
            top_k: Number of results to return
            show_details: Whether to show detailed scores
        """
        # Initialize ranker if needed
        if self.ranker is None:
            if not self.initialize_ranker():
                logger.error("Cannot search without ranker initialized")
                return
        
        # Load pages data if needed
        if self.pages_data is None:
            self.pages_data, _ = WikipediaCrawler.load_data()
        
        # Perform search
        logger.info(f"\nSearching for: '{query}'")
        logger.info("="*80)
        
        results = self.ranker.search(query, top_k=top_k, return_details=True)
        
        if not results:
            print("\nNo results found.")
            return
        
        # Display results
        print(f"\nFound {len(results)} results:\n")
        
        for i, (title, combined, text, pr) in enumerate(results, 1):
            print(f"{i}. {title}")
            
            if show_details:
                print(f"   Combined Score: {combined:.4f}")
                print(f"   Text Relevance: {text:.4f}")
                print(f"   PageRank: {pr:.4f}")
            
            # Show summary if available
            if title in self.pages_data:
                summary = self.pages_data[title].get('summary', '')
                if summary:
                    print(f"   {summary[:150]}...")
            
            print()
    
    def run_evaluation(self) -> bool:
        """
        Step 5: Run evaluation (Kundan's component)
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 5: RUNNING EVALUATION (Kundan's Component)")
        logger.info("="*80)
        
        try:
            # Initialize ranker if needed
            if self.ranker is None:
                if not self.initialize_ranker():
                    return False
            
            # Create evaluator
            self.evaluator = SearchEvaluator(self.ranker)
            
            # Create relevance template
            logger.info("Creating relevance judgment template...")
            template = self.evaluator.create_relevance_template()
            self.evaluator.relevance_judgments = template
            self.evaluator.save_relevance_judgments()
            
            # Compare with/without PageRank
            logger.info("\nComparing results with and without PageRank...")
            self.evaluator.compare_with_without_pagerank(
                queries=["machine learning", "neural networks"]
            )
            
            # Measure performance
            performance = self.evaluator.measure_performance(iterations=3)
            logger.info(f"\nPerformance Metrics:")
            logger.info(f"  Mean response time: {performance['mean_response_time']*1000:.2f} ms")
            
            logger.info(f"\n✓ Evaluation complete")
            return True
            
        except Exception as e:
            logger.error(f"✗ Evaluation failed: {e}")
            return False
    
    def run_full_pipeline(self, max_pages: Optional[int] = None) -> bool:
        """
        Run the complete pipeline from crawling to evaluation
        
        Args:
            max_pages: Maximum pages to crawl
            
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        
        logger.info("\n" + "╔" + "="*78 + "╗")
        logger.info("║" + " "*20 + "FULL PIPELINE EXECUTION" + " "*35 + "║")
        logger.info("╚" + "="*78 + "╝\n")
        
        # Run all steps
        steps = [
            ("Crawling", lambda: self.crawl_wikipedia(max_pages)),
            ("PageRank", self.compute_pagerank),
            ("Indexing", self.build_index),
            ("Ranker Init", self.initialize_ranker),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                logger.error(f"Pipeline failed at step: {step_name}")
                return False
        
        # Test search
        logger.info("\n" + "="*80)
        logger.info("TESTING SEARCH")
        logger.info("="*80)
        self.search("machine learning", top_k=5)
        
        elapsed = time.time() - start_time
        logger.info(f"\n✓ Full pipeline completed in {elapsed/60:.2f} minutes")
        
        return True
    
    def start_web_server(self):
        """
        Start the Flask web interface
        """
        logger.info("Starting web server...")
        
        # Load search engine components
        if not load_search_engine():
            logger.error("Failed to load search engine. Run pipeline first!")
            return
        
        # Start server
        app.run(
            host=config.WEB_CONFIG['host'],
            port=config.WEB_CONFIG['port'],
            debug=config.WEB_CONFIG['debug']
        )


def main():
    """
    Main entry point with command-line interface
    """
    parser = argparse.ArgumentParser(
        description='PageRank Search Engine - Team Project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 -m Backend.main --full-pipeline              # Run everything
  python3 -m Backend.main --crawl --max-pages 250      # Crawl 250 pages (fast!)
  python3 -m Backend.main --search "machine learning"  # Search
  python3 -m Backend.main --serve                      # Start web server
        """
    )
    
    # Pipeline options
    parser.add_argument('--full-pipeline', action='store_true',
                       help='Run complete pipeline (crawl, pagerank, index, rank)')
    parser.add_argument('--crawl', action='store_true',
                       help='Run crawler only (uses fast WikipediaCrawler)')
    parser.add_argument('--pagerank', action='store_true',
                       help='Compute PageRank only')
    parser.add_argument('--index', action='store_true',
                       help='Build search index only')
    parser.add_argument('--evaluate', action='store_true',
                       help='Run evaluation only')
    
    # Search options
    parser.add_argument('--search', type=str,
                       help='Perform a search query')
    parser.add_argument('--top-k', type=int, default=10,
                       help='Number of search results (default: 10)')
    
    # Server option
    parser.add_argument('--serve', action='store_true',
                       help='Start web server')
    
    # Configuration
    parser.add_argument('--max-pages', type=int,
                       help='Maximum pages to crawl')
    
    args = parser.parse_args()
    
    # Create engine instance
    engine = PageRankSearchEngine()
    
    # Execute based on arguments
    try:
        if args.full_pipeline:
            # Run complete pipeline
            engine.run_full_pipeline(max_pages=args.max_pages)
            
        elif args.crawl:
            # Run crawler only (WikipediaCrawler)
            engine.crawl_wikipedia(max_pages=args.max_pages)
            
        elif args.pagerank:
            # Compute PageRank only
            engine.compute_pagerank()
            
        elif args.index:
            # Build index only
            engine.build_index()
            
        elif args.evaluate:
            # Run evaluation only
            engine.run_evaluation()
            
        elif args.search:
            # Perform search
            engine.search(args.search, top_k=args.top_k)
            
        elif args.serve:
            # Start web server
            engine.start_web_server()
            
        else:
            # No arguments - show help and run interactive mode
            parser.print_help()
            print("\n" + "="*80)
            print("Interactive Mode")
            print("="*80)
            print("\nWhat would you like to do?")
            print("1. Run full pipeline")
            print("2. Search")
            print("3. Start web server")
            print("4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                max_pages_input = input("Max pages to crawl (default 250): ").strip()
                max_pages = int(max_pages_input) if max_pages_input else None
                engine.run_full_pipeline(max_pages=max_pages)
                
            elif choice == '2':
                query = input("Enter search query: ").strip()
                if query:
                    engine.search(query)
                    
            elif choice == '3':
                engine.start_web_server()
                
            elif choice == '4':
                print("Goodbye!")
                sys.exit(0)
                
            else:
                print("Invalid choice")
                
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()