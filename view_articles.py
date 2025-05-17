from pymongo import MongoClient
from pprint import pprint

client = MongoClient("mongodb://localhost:27017")
db = client["news_dashboard"]
collection = db["articles"]

print("[INFO] Latest Articles:")
for article in collection.find().sort("published_at", -1).limit(10):
    pprint(article)
