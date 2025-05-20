"""
Main entry point for the news scraper system.
Allows running individual components or the full system.
"""
import sys
import argparse
import logging
from typing import Dict, Any

# Import components
from scraper import get_article_links, scrape_article, SOURCES
from summarizer import summarize_text
from fetch_and_store import fetch_all_sources, process_source, clean_old_articles
from scheduler import start_scheduler, stop_scheduler, generate_status_report
from db import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("main")

def test_scraper(source_name: str = None):
    """Test the scraper functionality"""
    if source_name and source_name not in SOURCES:
        logger.error(f"Source '{source_name}' not found. Available sources: {', '.join(SOURCES.keys())}")
        return
    
    sources_to_test = [source_name] if source_name else SOURCES.keys()
    
    for src in sources_to_test:
        logger.info(f"Testing scraper for {src}")
        links = get_article_links(src, SOURCES[src])
        
        if not links:
            logger.warning(f"No links found for {src}")
            continue
            
        logger.info(f"Found {len(links)} links for {src}")
        
        # Test scraping the first article
        if links:
            logger.info(f"Testing article scraping for {links[0]}")
            article = scrape_article(links[0])
            
            if article and article.get("title"):
                logger.info(f"Successfully scraped: {article['title']}")
                
                # Test summarization
                if article.get("text"):
                    summary = summarize_text(article["text"], source=src)
                    logger.info(f"Summary: {summary[:100]}...")
            else:
                logger.error(f"Failed to scrape article from {links[0]}")

def run_fetch_job():
    """Run a single fetch job across all sources"""
    results = fetch_all_sources()
    total = sum(results.values())
    logger.info(f"Fetch job complete: {total} articles fetched")
    
    for source, count in results.items():
        logger.info(f"  - {source}: {count} articles")
    
    return results

def display_database_stats():
    """Show database statistics"""
    try:
        article_count = db_manager.articles.count_documents({})
        sources = db_manager.get_sources()
        categories = db_manager.get_categories()
        source_counts = db_manager.get_article_counts_by_source()
        category_counts = db_manager.get_article_counts_by_category()
        
        print("\n=== Database Statistics ===")
        print(f"Total articles: {article_count}")
        print(f"Number of sources: {len(sources)}")
        print(f"Number of categories: {len(categories)}")
        
        print("\nArticles by source:")
        for source, count in source_counts.items():
            print(f"  - {source}: {count}")
            
        print("\nArticles by category:")
        for category, count in category_counts.items():
            print(f"  - {category}: {count}")
            
    except Exception as e:
        logger.error(f"Error displaying database stats: {e}")

def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(description="News Scraper System")
    
    # Define commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Test scraper command
    test_parser = subparsers.add_parser("test", help="Test the scraper")
    test_parser.add_argument("--source", help="Source to test (default: all)")
    
    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Run a fetch job")
    fetch_parser.add_argument("--source", help="Source to fetch (default: all)")
    
    # Schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Run the scheduler")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Display database statistics")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old articles")
    cleanup_parser.add_argument("--days", type=int, default=30, help="Age threshold in days (default: 30)")
    
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == "test":
        test_scraper(args.source)
    elif args.command == "fetch":
        if args.source:
            process_source(args.source, SOURCES[args.source])
        else:
            run_fetch_job()
    elif args.command == "schedule":
        try:
            logger.info("Starting scheduler (press Ctrl+C to stop)")
            start_scheduler()
            # Keep the main thread alive
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping scheduler...")
                stop_scheduler()
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
    elif args.command == "stats":
        display_database_stats()
    elif args.command == "cleanup":
        count = clean_old_articles(days=args.days)
        logger.info(f"Removed {count} old articles")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()