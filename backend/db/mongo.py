from pymongo import MongoClient, ASCENDING, DESCENDING, UpdateOne
from pymongo.errors import BulkWriteError
from datetime import datetime
from dateutil.parser import parse as parse_date
import os
import json

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "news_dashboard"
COLLECTION_NAME = "articles"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
articles_col = db[COLLECTION_NAME]

# Ensure indexes for fast queries and uniqueness
def ensure_indexes():
    articles_col.create_index("url", unique=True)
    articles_col.create_index([("published_at", DESCENDING)])

ensure_indexes()

def upsert_articles(article_list):
    """
    Insert or update articles in bulk based on unique URL.
    article_list: list of dicts with article data.
    """
    if not article_list:
        print("[INFO] No articles to upsert.")
        return

    operations = []
    for article in article_list:
        # Defensive: parse date string if needed
        pub_date = article.get("published_at")
        if isinstance(pub_date, str):
            try:
                article["published_at"] = parse_date(pub_date)
            except Exception as e:
                print(f"[WARN] Skipping article due to invalid date: {pub_date}")
                continue

        if not article.get("url"):
            print(f"[WARN] Skipping article with missing URL: {article}")
            continue

        filter_ = {"url": article["url"]}
        update_ = {"$set": article}
        operations.append(UpdateOne(filter_, update_, upsert=True))

    if not operations:
        print("[INFO] No valid operations to perform.")
        return

    try:
        result = articles_col.bulk_write(operations)
        print(f"[INFO] ✅ Upserted {result.upserted_count} articles, Modified {result.modified_count} articles.")
    except BulkWriteError as bwe:
        print("[ERROR] ❌ Bulk write error:")
        print(json.dumps(bwe.details, indent=2))

def get_latest_articles(limit=20):
    """
    Fetch latest articles sorted by published_at descending.
    """
    cursor = articles_col.find().sort("published_at", DESCENDING).limit(limit)
    articles = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        articles.append(doc)
    return articles

# Optional CLI test
if __name__ == "__main__":
    print("[DEBUG] Connected to DB:", db.name)
    print("[DEBUG] Collection:", COLLECTION_NAME)
    print("[DEBUG] Document count:", articles_col.count_documents({}))
    print("[DEBUG] Latest articles:")
    for article in get_latest_articles(limit=5):
        print(f" - {article.get('title')} | {article.get('published_at')}")
