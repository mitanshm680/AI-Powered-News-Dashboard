from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/NEWS_SUMMARY_DASHBOARD")
client = MongoClient(MONGODB_URI)
db = client.get_database()  # Will use the database from URI or default
articles_collection = db.articles