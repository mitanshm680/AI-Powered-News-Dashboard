# tests/smoke_test.py
from backend.scrapers.multi_source_scraper import MultiSourceScraper
from backend.utils.logger import log


def run_smoke_test():
    log.info("🚦 Running smoke test...")
    scraper = MultiSourceScraper()
    articles = scraper.scrape()

    valid_articles = [a for a in articles if a]
    count = len(valid_articles)

    if count == 0:
        log.error("❌ Smoke test failed: No valid articles were scraped.")
        return False

    log.info(f"✅ Smoke test passed: {count} valid articles scraped.")
    for a in valid_articles[:3]:  # Show a sample
        log.info(f"- {a['source']} | {a['title'][:60]}...")

    return True
