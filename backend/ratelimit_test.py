"""
Test suite for news scraper system with rate limiting verification
"""
import time
import logging
from datetime import datetime
from typing import List, Dict
import concurrent.futures

from scraper import get_article_links, scrape_article, SOURCES
from summarizer import summarize_text, wait_for_rate_limit, api_calls
from fetch_and_store import process_source

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test")

def test_rate_limiting():
    """Test if rate limiting is working correctly."""
    logger.info("Testing rate limiting...")
    
    # Test text to summarize
    test_text = "This is a test article. It contains multiple sentences. Testing rate limiting."
    
    # Try to make requests faster than the rate limit
    start_time = time.time()
    request_times: List[float] = []
    completion_times: List[float] = []  # Track when each request completes
    
    for i in range(20):  # Try to make 20 requests (more than the 15 RPM limit)
        logger.info(f"Making request {i+1}/20")
        before_request = time.time()
        summary = summarize_text(test_text, source="Test", category="test")
        after_request = time.time()
        
        request_times.append(after_request - before_request)
        completion_times.append(after_request)
        
        if summary:
            logger.info(f"Summary {i+1}: {summary[:50]}...")
        else:
            logger.warning(f"Failed to get summary for request {i+1}")
    
    total_time = time.time() - start_time
    
    # Analyze results
    logger.info(f"\nRate Limiting Test Results:")
    logger.info(f"Total time: {total_time:.2f} seconds")
    logger.info(f"Average request time: {sum(request_times)/len(request_times):.2f} seconds")
    
    # Check the maximum rate in any 60-second window
    max_requests_per_minute = 0
    for i in range(len(completion_times)):
        window_start = completion_times[i]
        requests_in_window = 1
        
        # Count requests within 60 seconds after this request
        for j in range(i + 1, len(completion_times)):
            if completion_times[j] - window_start <= 60:
                requests_in_window += 1
            else:
                break
        
        max_requests_per_minute = max(max_requests_per_minute, requests_in_window)
    
    logger.info(f"Maximum requests in any 60-second window: {max_requests_per_minute}")
    
    # Verify we didn't exceed rate limit in any 60-second window
    assert max_requests_per_minute <= 12, f"Rate limit exceeded: {max_requests_per_minute} requests in a 60-second window"
    
    logger.info("Rate limiting test passed successfully!")

def test_parallel_processing():
    """Test parallel processing with rate limiting."""
    logger.info("\nTesting parallel processing with rate limiting...")
    
    # Get some test articles
    source = "Reuters"  # Using Reuters as test source
    links = get_article_links(source, SOURCES[source])
    
    if not links:
        logger.error("No test articles found!")
        return
    
    # Take first 5 articles for testing
    test_links = links[:5]
    logger.info(f"Testing with {len(test_links)} articles")
    
    # Process articles in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(process_article, url): url for url in test_links}
        
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                if result:
                    logger.info(f"Successfully processed: {url}")
                else:
                    logger.warning(f"Failed to process: {url}")
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
    
    logger.info("Parallel processing test completed!")

def process_article(url: str) -> bool:
    """Process a single article for testing."""
    try:
        # Scrape
        article_data = scrape_article(url)
        if not article_data:
            return False
            
        # Summarize
        summary = summarize_text(
            article_data["text"], 
            source=article_data.get("source", ""),
            category=article_data.get("category", "general")
        )
        
        return bool(summary)
    except Exception as e:
        logger.error(f"Error in process_article: {e}")
        return False

def test_batch_processing():
    """Test batch processing with rate limiting."""
    logger.info("\nTesting batch processing...")
    
    # Configuration
    batch_size = 5
    total_articles = 12  # Will create 3 batches
    
    # Generate test data
    test_data = [
        f"Test article {i}. This is a longer sentence to make the text more realistic. "
        f"Adding more content to simulate a real article. Testing batch {i//batch_size + 1}."
        for i in range(total_articles)
    ]
    
    start_time = time.time()
    summaries = []
    
    # Process in batches
    for i in range(0, len(test_data), batch_size):
        batch = test_data[i:i + batch_size]
        logger.info(f"\nProcessing batch {i//batch_size + 1}")
        
        batch_start = time.time()
        for article in batch:
            summary = summarize_text(article, source="Test", category="test")
            if summary:
                summaries.append(summary)
        batch_time = time.time() - batch_start
        
        logger.info(f"Batch {i//batch_size + 1} completed in {batch_time:.2f} seconds")
        
        # If there are more batches, wait a bit
        if i + batch_size < len(test_data):
            wait_time = 5
            logger.info(f"Waiting {wait_time} seconds before next batch...")
            time.sleep(wait_time)
    
    total_time = time.time() - start_time
    
    logger.info(f"\nBatch Processing Results:")
    logger.info(f"Total articles: {total_articles}")
    logger.info(f"Successful summaries: {len(summaries)}")
    logger.info(f"Total time: {total_time:.2f} seconds")
    logger.info(f"Average time per article: {total_time/total_articles:.2f} seconds")

def main():
    """Run all tests."""
    try:
        logger.info("Starting tests...")
        
        # Test rate limiting
        test_rate_limiting()
        
        # Test parallel processing
        test_parallel_processing()
        
        # Test batch processing
        test_batch_processing()
        
        logger.info("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    main() 