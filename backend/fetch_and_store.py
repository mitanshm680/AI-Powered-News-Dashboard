"""
Enhanced module for fetching, processing and storing news articles
"""
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper import SOURCES, get_article_links, scrape_article
from summarizer import summarize_text
from models import create_article_dict
from db import articles_collection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler("news_fetcher.log")]
)
logger = logging.getLogger("fetch_and_store")

# Maximum number of worker threads
MAX_WORKERS = 5

# Maximum articles to process per source
MAX_ARTICLES_PER_SOURCE = 15

def article_exists(url: str) -> bool:
    """Check if an article with the given URL already exists in the database."""
    return articles_collection.find_one({"fullArticleUrl": url}) is not None

def analyze_sentiment(text: str) -> str:
    """
    Simple sentiment analysis of text.
    Returns: "positive", "negative", or "neutral"
    """
    # Simple keyword-based sentiment analysis
    # In a production environment, use a proper NLP model
    positive_words = ["good", "great", "excellent", "positive", "success", "happy", "win", "breakthrough"]
    negative_words = ["bad", "terrible", "negative", "failure", "sad", "lose", "crisis", "disaster", "death"]
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"

def process_article(url: str, source_name: str) -> Optional[Dict[str, Any]]:
    """Process a single article URL - scrape, summarize, analyze."""
    try:
        # Skip if article already exists
        if article_exists(url):
            logger.debug(f"Article already exists: {url}")
            return None
            
        # Scrape the article
        scraped = scrape_article(url)
        if not scraped or not scraped.get("text"):
            logger.warning(f"Failed to scrape article: {url}")
            return None
            
        # Get the category
        category = scraped.get("category", "general")
        
        # Generate summary
        summary = summarize_text(
            scraped["text"], 
            source=source_name,
            category=category
        )
        
        # Analyze sentiment
        sentiment = analyze_sentiment(scraped["text"])
        
        # Create article document
        article_doc = create_article_dict(
            title=scraped["title"],
            summary=summary,
            full_text=scraped["text"],
            url=url,
            image_url=scraped.get("image_url", ""),
            source=source_name,
            published_at=scraped.get("published_at"),
            category=category,
            keywords=scraped.get("keywords", []),
            sentiment=sentiment
        )
        
        return article_doc
        
    except Exception as e:
        logger.error(f"Error processing article {url}: {e}")
        return None

def store_article(article_doc: Dict[str, Any]) -> bool:
    """Store an article in the database."""
    try:
        result = articles_collection.insert_one(article_doc)
        logger.info(f"[✅] Stored: {article_doc['title']} (ID: {result.inserted_id})")
        return True
    except Exception as e:
        logger.error(f"Error storing article {article_doc['title']}: {e}")
        return False

def process_source(source_name: str, feed_url: str) -> int:
    """
    Process a single news source.
    
    Returns:
        Number of articles successfully stored
    """
    logger.info(f"Processing source: {source_name}")
    try:
        # Get article links
        links = get_article_links(source_name, feed_url)
        if not links:
            logger.warning(f"No links found for {source_name}")
            return 0
            
        # Limit number of articles to process
        links = links[:MAX_ARTICLES_PER_SOURCE]
        logger.info(f"Processing {len(links)} articles from {source_name}")
        
        articles_stored = 0
        
        # Process articles in parallel with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(process_article, url, source_name): url 
                for url in links
            }
            
            # Process completed tasks
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    article_doc = future.result()
                    if article_doc:
                        if store_article(article_doc):
                            articles_stored += 1
                except Exception as e:
                    logger.error(f"Exception processing {url}: {e}")
        
        logger.info(f"Completed {source_name}: {articles_stored} new articles stored")
        return articles_stored
        
    except Exception as e:
        logger.error(f"Error processing source {source_name}: {e}")
        return 0

def clean_old_articles(days: int = 30) -> int:
    """
    Remove articles older than specified days.
    
    Args:
        days: Number of days to keep articles
        
    Returns:
        Number of articles removed
    """
    try:
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        result = articles_collection.delete_many({
            "createdAt": {"$lt": cutoff_date},
            "saved": False  # Don't delete saved articles
        })
        
        deleted_count = result.deleted_count
        logger.info(f"Cleaned {deleted_count} articles older than {days} days")
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning old articles: {e}")
        return 0

def fetch_all_sources() -> Dict[str, int]:
    """
    Fetch articles from all sources.
    
    Returns:
        Dictionary with source names as keys and number of articles stored as values
    """
    results = {}
    start_time = time.time()
    
    for name, url in SOURCES.items():
        articles_stored = process_source(name, url)
        results[name] = articles_stored
        
        # Add a small delay between sources to be polite
        time.sleep(2)
    
    # Clean old articles
    clean_old_articles()
    
    elapsed_time = time.time() - start_time
    logger.info(f"Fetch completed in {elapsed_time:.2f} seconds")
    
    return results

if __name__ == "__main__":
    results = fetch_all_sources()
    total_articles = sum(results.values())
    print(f"Total articles fetched: {total_articles}")
    for source, count in results.items():
        print(f"  - {source}: {count} articles")