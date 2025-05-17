import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.scrapers.multi_source_scraper import MultiSourceScraper
from backend.db.mongo import upsert_articles
from backend.utils.logger import log  # Assuming you have a logger set up


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
            break  # success - exit retry loop
        except Exception as e:
            log.error(f"Scraping attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(10)  # wait 10 seconds before retry
            else:
                log.error("Max retries reached. Skipping this cycle.")


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        job_scrape,
        trigger=IntervalTrigger(minutes=45),  # Run every 45 minutes
        id="scraper_job",
        replace_existing=True,
    )

    scheduler.start()
    log.info("Scheduler started. Scraper job will run every 45 minutes.")

    try:
        while True:
            time.sleep(3600)  # sleep and keep scheduler alive
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        log.info("Scheduler stopped.")


if __name__ == "__main__":
    start_scheduler()
