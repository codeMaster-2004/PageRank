"""
Automated Pipeline Runner
Runs the entire PageRank search engine pipeline in sequence

Usage:
    python run_pipeline.py              # Run full pipeline
    python run_pipeline.py --quick      # Skip crawling (use existing data)
    python run_pipeline.py --evaluate   # Include evaluation step
"""

import sys
import logging
import argparse
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_crawler(max_pages=None):
    """
    Step 1: Crawl Wikipedia pages
    """
    logger.info("="*80)
    logger.info("STEP 1: CRAWLING WIKIPEDIA PAGES")
    logger.info("="*80)
    
    try:
        from crawler import WikipediaCrawler
        
        crawler = WikipediaCrawler(max_pages=max_pages) if max_pages else WikipediaCrawler()
        pages_data, link_graph = crawler.crawl()
        crawler.save_data()
        
        logger.info(f"✓ Crawled {len(pages_data)} pages successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Crawler failed: {e}")
        return False


def run_pagerank():
    """
    Step 2: Compute PageRank scores
    """
    logger.info("\n" + "="*80)
    logger.info("STEP 2: COMPUTING PAGERANK")
    logger.info("="*80)
    
    try:
        from crawler import WikipediaCrawler
        from pagerank import PageRank
        
        # Load link graph
        _, link_graph = WikipediaCrawler.load_data()
        
        # Compute PageRank
        pr = PageRank()
        scores = pr.compute(link_graph)
        pr.save()
        
        logger.info(f"✓ PageRank computed successfully")
        logger.info(f"  Converged in {pr.iterations_to_converge} iterations")
        logger.info(f"  Total pages ranked: {len(scores)}")
        return True
    except Exception as e:
        logger.error(f"✗ PageRank failed: {e}")
        return False


def run_indexer():
    """
    Step 3: Build BM25 index
    """
    logger.info("\n" + "="*80)
    logger.info("STEP 3: BUILDING SEARCH INDEX")
    logger.info("="*80)
    
    try:
        from crawler import WikipediaCrawler
        from indexer import BM25Indexer
        
        # Load pages
        pages_data, _ = WikipediaCrawler.load_data()
        
        # Build index
        indexer = BM25Indexer()
        indexer.build_index(pages_data)
        indexer.save()
        
        logger.info(f"✓ Index built successfully")
        logger.info(f"  Total terms indexed: {len(indexer.inverted_index)}")
        logger.info(f"  Average document length: {indexer.avg_doc_length:.2f}")
        return True
    except Exception as e:
        logger.error(f"✗ Indexer failed: {e}")
        return False


def test_ranker():
    """
    Step 4: Test search ranking
    """
    logger.info("\n" + "="*80)
    logger.info("STEP 4: TESTING SEARCH RANKING")
    logger.info("="*80)
    
    try:
        from pagerank import PageRank
        from indexer import BM25Indexer
        from ranker import SearchRanker
        
        # Load components
        pagerank = PageRank.load()
        indexer = BM25Indexer.load()
        ranker = SearchRanker(pagerank, indexer)
        
        # Test with sample query
        test_query = "machine learning"
        results = ranker.search(test_query, top_k=5, return_details=True)
        
        logger.info(f"✓ Ranking engine tested successfully")
        logger.info(f"\n  Sample results for '{test_query}':")
        for i, (title, combined, text, pr) in enumerate(results, 1):
            logger.info(f"  {i}. {title}")
            logger.info(f"     Combined: {combined:.4f} | Text: {text:.4f} | PR: {pr:.4f}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Ranker test failed: {e}")
        return False


def run_evaluation():
    """
    Step 5: Run evaluation (optional)
    """
    logger.info("\n" + "="*80)
    logger.info("STEP 5: EVALUATION")
    logger.info("="*80)
    
    try:
        from pagerank import PageRank
        from indexer import BM25Indexer
        from ranker import SearchRanker
        from evaluator import SearchEvaluator
        
        # Load components
        pagerank = PageRank.load()
        indexer = BM25Indexer.load()
        ranker = SearchRanker(pagerank, indexer)
        
        # Create evaluator
        evaluator = SearchEvaluator(ranker)
        
        # Create relevance template
        template = evaluator.create_relevance_template()
        evaluator.relevance_judgments = template
        evaluator.save_relevance_judgments()
        
        # Compare with/without PageRank
        logger.info("\n  Comparing results with and without PageRank:")
        evaluator.compare_with_without_pagerank(queries=["machine learning", "neural networks"])
        
        # Measure performance
        performance = evaluator.measure_performance(iterations=3)
        logger.info(f"\n  Performance metrics:")
        logger.info(f"    Mean response time: {performance['mean_response_time']*1000:.2f} ms")
        logger.info(f"    Median response time: {performance['median_response_time']*1000:.2f} ms")
        
        logger.info(f"\n✓ Evaluation complete")
        logger.info(f"  Please edit results/relevance_judgments.json with your relevance ratings")
        logger.info(f"  Then run evaluator.py to see full evaluation metrics")
        return True
    except Exception as e:
        logger.error(f"✗ Evaluation failed: {e}")
        return False


def main():
    """
    Main pipeline execution
    """
    parser = argparse.ArgumentParser(description='Run PageRank Search Engine Pipeline')
    parser.add_argument('--quick', action='store_true', 
                       help='Skip crawling (use existing data)')
    parser.add_argument('--evaluate', action='store_true',
                       help='Include evaluation step')
    parser.add_argument('--max-pages', type=int, default=None,
                       help='Maximum pages to crawl (default: from config)')
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    logger.info("\n" + "╔" + "="*78 + "╗")
    logger.info("║" + " "*20 + "PAGERANK SEARCH ENGINE PIPELINE" + " "*27 + "║")
    logger.info("╚" + "="*78 + "╝\n")
    
    steps = []
    
    # Step 1: Crawling (optional)
    if not args.quick:
        if run_crawler(max_pages=args.max_pages):
            steps.append(("Crawling", "✓"))
        else:
            steps.append(("Crawling", "✗"))
            logger.error("Pipeline stopped due to crawler failure")
            return
    else:
        logger.info("Skipping crawling (using existing data)")
        steps.append(("Crawling", "⊙ Skipped"))
    
    # Step 2: PageRank
    if run_pagerank():
        steps.append(("PageRank", "✓"))
    else:
        steps.append(("PageRank", "✗"))
        logger.error("Pipeline stopped due to PageRank failure")
        return
    
    # Step 3: Indexing
    if run_indexer():
        steps.append(("Indexing", "✓"))
    else:
        steps.append(("Indexing", "✗"))
        logger.error("Pipeline stopped due to indexing failure")
        return
    
    # Step 4: Testing
    if test_ranker():
        steps.append(("Ranking Test", "✓"))
    else:
        steps.append(("Ranking Test", "✗"))
        logger.warning("Ranking test failed, but continuing...")
        steps.append(("Ranking Test", "⚠"))
    
    # Step 5: Evaluation (optional)
    if args.evaluate:
        if run_evaluation():
            steps.append(("Evaluation", "✓"))
        else:
            steps.append(("Evaluation", "✗"))
            logger.warning("Evaluation failed")
    
    # Summary
    elapsed_time = time.time() - start_time
    
    logger.info("\n" + "="*80)
    logger.info("PIPELINE SUMMARY")
    logger.info("="*80)
    
    for step_name, status in steps:
        logger.info(f"  {step_name:<20} {status}")
    
    logger.info(f"\n  Total time: {elapsed_time/60:.2f} minutes")
    
    # Next steps
    logger.info("\n" + "="*80)
    logger.info("NEXT STEPS")
    logger.info("="*80)
    logger.info("  1. Run the web interface:")
    logger.info("     $ python web_interface.py")
    logger.info("     Then open http://localhost:5000 in your browser")
    logger.info("")
    logger.info("  2. Test individual components:")
    logger.info("     $ python ranker.py      # Test search ranking")
    logger.info("     $ python evaluator.py   # Run evaluation")
    logger.info("")
    logger.info("  3. Customize settings in config.py")
    logger.info("="*80)


if __name__ == "__main__":
    main()