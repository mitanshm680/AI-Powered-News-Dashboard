from pymongo import MongoClient, ASCENDING, DESCENDING, UpdateOne
from pymongo.errors import BulkWriteError
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "news_dashboard"
COLLECTION_NAME = "articles"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
articles_col = db[COLLECTION_NAME]

# Ensure indexes for fast queries and uniqueness
def ensure_indexes():
    # Unique index on url to prevent duplicates
    articles_col.create_index("url", unique=True)
    # Index on published_at for sorting latest articles
    articles_col.create_index([("published_at", DESCENDING)])

ensure_indexes()

def upsert_articles(article_list):
    """
    Insert or update articles in bulk based on unique URL.
    article_list: list of dicts with article data.
    """
    if not article_list:
        return

    operations = []
    for article in article_list:
        filter_ = {"url": article.get("url")}
        update_ = {"$set": article}
        operations.append(UpdateOne(filter_, update_, upsert=True))

    try:
        result = articles_col.bulk_write(operations)
        print(f"Upserted {result.upserted_count} articles, Modified {result.modified_count} articles.")
    except BulkWriteError as bwe:
        print(f"Bulk write error: {bwe.details}")

def get_latest_articles(limit=20):
    """
    Fetch latest articles sorted by published_at descending.
    """
    cursor = articles_col.find().sort("published_at", DESCENDING).limit(limit)
    # Convert Mongo documents to JSON-serializable dicts
    articles = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        articles.append(doc)
    return articles
