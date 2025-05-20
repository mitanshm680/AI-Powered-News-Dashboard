from scraper import SOURCES, get_article_links, scrape_article
from summarizer import summarize_text
from models import create_article_dict
from db import articles_collection

def article_exists(url):
    return articles_collection.find_one({"fullArticleUrl": url}) is not None

def process_source(source_name, feed_url):
    print(f"[INFO] Processing source: {source_name}")
    links = get_article_links(source_name, feed_url)

    for url in links:
        if article_exists(url):
            continue

        scraped = scrape_article(url)
        if not scraped or not scraped.get("text"):
            continue

        summary = summarize_text(scraped["text"], source=source_name)

        article_doc = create_article_dict(
            title=scraped["title"],
            summary=summary,
            full_text=scraped["text"],
            url=url,
            image_url=scraped["image_url"],
            source=source_name,
            published_at=scraped["published_at"]
        )

        articles_collection.insert_one(article_doc)
        print(f"[✅] Stored: {scraped['title']}")

def fetch_all_sources():
    for name, url in SOURCES.items():
        process_source(name, url)

if __name__ == "__main__":
    fetch_all_sources()
