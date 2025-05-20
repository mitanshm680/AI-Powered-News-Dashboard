"""
Enhanced database module with connection pooling, indexes, and error handling
"""
import os
import logging
import time
from typing import Dict, Any, List, Optional, Union
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("database")

# Connection settings
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds

# MongoDB connection string
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/NEWS_SUMMARY_DASHBOARD")

# Database name (extract from URI or use default)
DB_NAME = os.getenv("DB_NAME", "news_dashboard")

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, uri: str = MONGODB_URI, db_name: str = DB_NAME):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.articles = None
        self.analytics = None
        self.connect()
    
    def connect(self) -> bool:
        """Establish connection to MongoDB and set up collections"""
        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                # Connect with connection pooling and timeouts
                self.client = MongoClient(
                    self.uri,
                    maxPoolSize=50,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=10000,
                    serverSelectionTimeoutMS=5000
                )
                
                # Force a command to check the connection
                self.client.admin.command('ping')
                
                # Get the database
                self.db = self.client.get_database(self.db_name)
                
                # Set up collections
                self.articles = self.db.articles
                self.analytics = self.db.analytics
                
                # Set up indexes
                self._setup_indexes()
                
                logger.info(f"Connected to MongoDB: {self.db_name}")
                return True
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.critical("Failed to connect to MongoDB after multiple attempts")
                    raise
        
        return False
    
    def _setup_indexes(self):
        """Set up database indexes for better query performance"""
        # Articles collection indexes
        self.articles.create_index([("fullArticleUrl", ASCENDING)], unique=True)
        self.articles.create_index([("source", ASCENDING)])
        self.articles.create_index([("category", ASCENDING)])
        self.articles.create_index([("publishedAt", DESCENDING)])
        self.articles.create_index([("createdAt", DESCENDING)])
        self.articles.create_index([("saved", ASCENDING)])
        self.articles.create_index([("viewCount", DESCENDING)])
        
        # Text search index
        self.articles.create_index([
            ("title", TEXT), 
            ("summary", TEXT), 
            ("full_text", TEXT)
        ])
        
        # Analytics collection indexes
        self.analytics.create_index([("date", DESCENDING)])
        self.analytics.create_index([("source", ASCENDING)])
        self.analytics.create_index([("category", ASCENDING)])
        
        logger.info("Database indexes created or confirmed")
    
    def find_article_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Find an article by its URL"""
        return self.articles.find_one({"fullArticleUrl": url})
    
    def find_articles(self, query: Dict[str, Any] = None, limit: int = 50, 
                    skip: int = 0, sort_by: str = "publishedAt", ascending: bool = False) -> List[Dict[str, Any]]:
        """Find articles based on query parameters"""
        if query is None:
            query = {}
            
        sort_direction = ASCENDING if ascending else DESCENDING
        
        return list(self.articles.find(
            query,
            {'full_text': 0}  # Exclude full text field for performance
        ).sort(sort_by, sort_direction).skip(skip).limit(limit))
    
    def search_articles(self, text: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search articles using text search"""
        return list(self.articles.find(
            {"$text": {"$search": text}},
            {"score": {"$meta": "textScore"}, "full_text": 0}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit))
    
    def get_article_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Get a single article by ID"""
        return self.articles.find_one({"id": article_id})
    
    def update_article(self, article_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an article by ID"""
        result = self.articles.update_one(
            {"id": article_id},
            {"$set": {**update_data, "updatedAt": time.time()}}
        )
        return result.modified_count > 0
    
    def increment_view_count(self, article_id: str) -> bool:
        """Increment article view count"""
        result = self.articles.update_one(
            {"id": article_id},
            {"$inc": {"viewCount": 1}, "$set": {"updatedAt": time.time()}}
        )
        return result.modified_count > 0
    
    def toggle_saved_status(self, article_id: str) -> bool:
        """Toggle saved status for an article"""
        article = self.get_article_by_id(article_id)
        if not article:
            return False
            
        new_status = not article.get("saved", False)
        result = self.articles.update_one(
            {"id": article_id},
            {"$set": {"saved": new_status, "updatedAt": time.time()}}
        )
        return result.modified_count > 0
    
    def get_categories(self) -> List[str]:
        """Get list of all categories in the database"""
        return self.articles.distinct("category")
    
    def get_sources(self) -> List[str]:
        """Get list of all sources in the database"""
        return self.articles.distinct("source")
    
    def get_article_counts_by_source(self) -> Dict[str, int]:
        """Get counts of articles by source"""
        result = {}
        for source in self.get_sources():
            result[source] = self.articles.count_documents({"source": source})
        return result
    
    def get_article_counts_by_category(self) -> Dict[str, int]:
        """Get counts of articles by category"""
        result = {}
        for category in self.get_categories():
            result[category] = self.articles.count_documents({"category": category})
        return result
    
    def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")


# Global database instance
db_manager = DatabaseManager()
articles_collection = db_manager.articles
analytics_collection = db_manager.analytics


# Clean up connection when program exits
import atexit
atexit.register(db_manager.close)


if __name__ == "__main__":
    # Test database connection
    try:
        print(f"Connected to database: {db_manager.db_name}")
        print(f"Articles collection exists: {db_manager.articles is not None}")
        print(f"Article count: {db_manager.articles.count_documents({})}")
        print(f"Categories: {db_manager.get_categories()}")
        print(f"Sources: {db_manager.get_sources()}")
    except Exception as e:
        print(f"Error connecting to database: {e}")