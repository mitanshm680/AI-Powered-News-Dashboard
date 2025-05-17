# backend/scheduler/scheduler.py
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.scrapers.multi_source_scraper import MultiSourceScraper
from backend.db.mongo import upsert_articles
from backend.utils.logger import log

# Create ONE global scheduler object so it isn’t created twice
scheduler_instance = BackgroundScheduler()

def job_scrape():
    log.info(f"Scraper job started at {datetime.utcnow().isoformat()} UTC")
    scraper = MultiSourceScraper()
    retries = 3
    for attempt in range(1, retries + 1):
        try:
            articles = scraper.scrape()
            if articles:
                upsert_articles(articles)
                log.info(f"Scraped and stored {len(articles)} articles successfully.")
            else:
                log.info("No articles scraped this run.")
            break
        except Exception as e:
            log.error(f"Scraping attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(10)
            else:
                log.error("Max retries reached. Skipping this cycle.")

def start_scheduler():
    """
    Start the APScheduler if not already running.
    Non‑blocking: returns immediately, so you can call it from FastAPI startup.
    """
    if not scheduler_instance.running:
        scheduler_instance.add_job(
            job_scrape,
            trigger=IntervalTrigger(minutes=45),
            id="scraper_job",
            replace_existing=True,
        )
        scheduler_instance.start()
        log.info("Scheduler started. Scraper job will run every 45 minutes.")

# --- CLI / Stand‑alone mode -----------------------------------------------
if __name__ == "__main__":
    start_scheduler()         # start & return immediately
    try:
        while True:           # keep process alive
            time.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler_instance.shutdown()
        log.info("Scheduler stopped.")
