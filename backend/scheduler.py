"""
Advanced scheduler for news fetching with configurable intervals and monitoring.
"""
import time
import schedule
import threading
import logging
import os
import signal
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Callable, List

from fetch_and_store import fetch_all_sources, clean_old_articles, process_source
from scraper import get_article_links, SOURCES
from db import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scheduler.log")
    ]
)
logger = logging.getLogger("scheduler")

# Configuration
DEFAULT_CONFIG = {
    "fetch_interval_minutes": 30,
    "cleanup_interval_hours": 12,
    "cleanup_days_threshold": 30,
    "max_consecutive_failures": 3,
    "hours_to_pause_after_failures": 1,
    "max_articles_per_batch": 10,  # Limit articles per batch to stay under Gemini's rate limit
    "batch_processing_delay": 70  # Wait 60 seconds between batches to respect rate limit
}

# Path to config and status files
CONFIG_PATH = Path("config.json")
STATUS_PATH = Path("scheduler_status.json")

# Job status tracking
job_status = {
    "last_run": None,
    "last_success": None,
    "consecutive_failures": 0,
    "total_runs": 0,
    "total_successes": 0,
    "total_failures": 0,
    "articles_fetched": 0,
    "is_paused": False,
    "pause_until": None
}

# Thread for running the scheduler
scheduler_thread = None
running = False

def load_config() -> Dict[str, Any]:
    """Load configuration from file or use defaults"""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                logger.info("Loaded configuration from file")
                return {**DEFAULT_CONFIG, **config}  # Merge with defaults
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    # Use default if file doesn't exist or is invalid
    logger.info("Using default configuration")
    return DEFAULT_CONFIG

def save_status():
    """Save current job status to file"""
    try:
        with open(STATUS_PATH, 'w') as f:
            json.dump(job_status, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Error saving status: {e}")

def load_status():
    """Load previous job status from file"""
    global job_status
    if STATUS_PATH.exists():
        try:
            with open(STATUS_PATH, 'r') as f:
                stored_status = json.load(f)
                job_status.update(stored_status)
                logger.info("Loaded previous job status")
        except Exception as e:
            logger.error(f"Error loading status: {e}")

def run_with_error_handling(job_func: Callable):
    """Run a job with error handling and status tracking"""
    global job_status
    
    # Check if we're in a pause period
    if job_status["is_paused"] and job_status["pause_until"]:
        pause_until = datetime.fromisoformat(job_status["pause_until"] 
                                         if isinstance(job_status["pause_until"], str) 
                                         else job_status["pause_until"])
        
        if datetime.utcnow() < pause_until:
            logger.info(f"Scheduler is paused until {pause_until}")
            return
        else:
            # Resume operations
            job_status["is_paused"] = False
            job_status["pause_until"] = None
            logger.info("Resuming scheduled operations after pause period")
    
    job_status["last_run"] = datetime.utcnow().isoformat()
    job_status["total_runs"] += 1
    
    try:
        logger.info(f"Running scheduled job: {job_func.__name__}")
        result = job_func()
        
        # Update status on success
        job_status["last_success"] = datetime.utcnow().isoformat()
        job_status["consecutive_failures"] = 0
        job_status["total_successes"] += 1
        
        # Track articles fetched for fetch_all_sources
        if job_func.__name__ == "fetch_all_sources" and isinstance(result, dict):
            articles_fetched = sum(result.values())
            job_status["articles_fetched"] += articles_fetched
            logger.info(f"Fetched {articles_fetched} articles")
            
        logger.info(f"Successfully completed job: {job_func.__name__}")
        
    except Exception as e:
        job_status["consecutive_failures"] += 1
        job_status["total_failures"] += 1
        logger.error(f"Job failed: {job_func.__name__} | Error: {e}")
        
        # Check if we need to pause due to repeated failures
        config = load_config()
        if job_status["consecutive_failures"] >= config["max_consecutive_failures"]:
            pause_hours = config["hours_to_pause_after_failures"]
            pause_until = datetime.utcnow() + timedelta(hours=pause_hours)
            job_status["is_paused"] = True
            job_status["pause_until"] = pause_until.isoformat()
            logger.warning(f"Too many consecutive failures. Pausing operations for {pause_hours} hours until {pause_until}")
    
    # Save the updated status
    save_status()
    
    # Generate periodic status report
    if job_status["total_runs"] % 10 == 0:
        generate_status_report()

def fetch_job():
    """Wrapper for the fetch job with error handling and rate limiting"""
    config = load_config()
    
    def rate_limited_fetch():
        """Fetch articles with rate limiting"""
        results = {}
        for source, url in SOURCES.items():
            # Process source and get links
            links = get_article_links(source, url)
            if not links:
                continue
                
            # Process articles in smaller batches to respect rate limits
            batch_size = config["max_articles_per_batch"]
            for i in range(0, len(links), batch_size):
                batch = links[i:i + batch_size]
                batch_results = process_source_batch(source, batch)
                results[source] = results.get(source, 0) + batch_results
                
                # Wait between batches to respect rate limits
                if i + batch_size < len(links):
                    logger.info(f"Waiting {config['batch_processing_delay']} seconds before next batch...")
                    time.sleep(config['batch_processing_delay'])
        
        return results
    
    run_with_error_handling(rate_limited_fetch)

def cleanup_job():
    """Wrapper for the cleanup job with error handling"""
    config = load_config()
    days = config["cleanup_days_threshold"]
    
    def do_cleanup():
        return clean_old_articles(days=days)
    
    run_with_error_handling(do_cleanup)

def generate_status_report():
    """Generate a status report for monitoring"""
    try:
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": (datetime.utcnow() - start_time).total_seconds() / 3600.0,
            "database": {
                "status": "connected" if db_manager.client else "disconnected",
                "article_count": db_manager.articles.count_documents({}) if db_manager.articles else 0,
                "sources": db_manager.get_sources() if db_manager.articles else [],
                "categories": db_manager.get_categories() if db_manager.articles else []
            },
            "jobs": {
                "total_runs": job_status["total_runs"],
                "success_rate": (job_status["total_successes"] / job_status["total_runs"] * 100) 
                                if job_status["total_runs"] > 0 else 0,
                "articles_fetched": job_status["articles_fetched"],
                "last_success": job_status["last_success"],
                "is_paused": job_status["is_paused"],
                "pause_until": job_status["pause_until"]
            }
        }
        
        logger.info(f"Status Report: Success rate {report['jobs']['success_rate']:.1f}%, "
                   f"Articles: {report['database']['article_count']}, "
                   f"Uptime: {report['uptime']:.1f} hours")
                   
        # Save detailed report to file
        with open("status_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
            
    except Exception as e:
        logger.error(f"Error generating status report: {e}")

def configure_scheduler():
    """Configure and start the scheduler based on settings"""
    config = load_config()
    
    # Schedule the fetch job
    fetch_minutes = config["fetch_interval_minutes"]
    schedule.every(fetch_minutes).minutes.do(fetch_job)
    logger.info(f"Scheduled fetch job every {fetch_minutes} minutes")
    
    # Schedule the cleanup job
    cleanup_hours = config["cleanup_interval_hours"]
    schedule.every(cleanup_hours).hours.do(cleanup_job)
    logger.info(f"Scheduled cleanup job every {cleanup_hours} hours")
    
    # Also schedule a daily status report
    schedule.every().day.at("00:00").do(generate_status_report)

def run_scheduler():
    """Run the scheduler in a loop"""
    global running
    logger.info("Starting scheduler")
    
    while running:
        schedule.run_pending()
        time.sleep(1)
        
    logger.info("Scheduler stopped")

def start_scheduler():
    """Start the scheduler in a background thread"""
    global scheduler_thread, running
    
    if scheduler_thread and scheduler_thread.is_alive():
        logger.warning("Scheduler is already running")
        return
    
    running = True
    load_status()
    configure_scheduler()
    
    # Run the fetch job immediately on startup
    fetch_job()
    
    # Start the scheduler thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info("Scheduler started in background thread")

def stop_scheduler():
    """Stop the scheduler"""
    global running
    running = False
    logger.info("Stopping scheduler...")
    save_status()

def handle_signal(signum, frame):
    """Handle termination signals gracefully"""
    logger.info(f"Received signal {signum}. Shutting down...")
    stop_scheduler()
    exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

# Track start time for uptime calculation
start_time = datetime.utcnow()

def process_source_batch(source: str, links: List[str]) -> int:
    """Process a batch of articles from a source with rate limiting."""
    articles_stored = 0
    for link in links:
        try:
            # Process single article
            if process_source(source, {source: link}):
                articles_stored += 1
        except Exception as e:
            logger.error(f"Error processing article {link}: {e}")
    return articles_stored

if __name__ == "__main__":
    try:
        logger.info("News scraper scheduler starting up")
        logger.info(f"Current configuration: {load_config()}")
        
        # Start the scheduler
        start_scheduler()
        
        # Keep the main thread alive
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        stop_scheduler()
        logger.info("News scraper scheduler shut down")