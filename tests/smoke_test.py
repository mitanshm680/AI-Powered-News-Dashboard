from backend.scrapers.multi_source_scraper import MultiSourceScraper
from backend.utils.logger import log

def run_smoke_test() -> bool:
    log.info("🚦 Running smoke test …")
    scraper = MultiSourceScraper()
    articles = [a for a in scraper.scrape() if a]

    if not articles:
        log.error("❌ Smoke test failed: no valid articles.")
        return False

    log.info(f"✅ Smoke test passed: {len(articles)} valid articles scraped.")
    for art in articles[:3]:  # show a sample
        log.info(f"- {art['source']} | {art['title'][:70]}…")
    return True
