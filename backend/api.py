"""
Enhanced FastAPI backend for SmartBrief News Dashboard
Provides robust API endpoints with error handling, validation, and comprehensive features.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query, Path, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator, constr
from pydantic.json import timedelta_isoformat

from db import db_manager, articles_collection
from models import create_article_dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler("api.log")]
)
logger = logging.getLogger("api")

# API configuration
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"
API_TITLE = "SmartBrief News API"
API_DESCRIPTION = "API for accessing and managing news articles from multiple sources"

# Initialize FastAPI
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=f"{API_PREFIX}/openapi.json"
)

# CORS configuration
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Security (optional)
API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Base models for request/response
class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    code: int
    details: Optional[Dict] = None

class SuccessResponse(BaseModel):
    status: str = "success"
    data: Any

# API Models
class ArticleBase(BaseModel):
    title: str
    summary: str
    category: str 
    source: str
    imageUrl: Optional[str] = None
    fullArticleUrl: str
    publishedAt: str

class ArticleOut(ArticleBase):
    id: str
    saved: bool = False
    viewCount: Optional[int] = 0
    readTimeMinutes: Optional[int] = None

    class Config:
        schema_extra = {
            "example": {
                "id": "12345",
                "title": "New Research Reveals Promise in Climate Solutions",
                "summary": "Scientists have discovered a new method to reduce carbon emissions...",
                "category": "science",
                "source": "NewScience",
                "imageUrl": "https://example.com/image.jpg",
                "fullArticleUrl": "https://example.com/article",
                "publishedAt": "2023-04-15T14:30:00Z",
                "saved": False,
                "viewCount": 5,
                "readTimeMinutes": 4
            }
        }

class ArticleList(BaseModel):
    articles: List[ArticleOut]
    totalCount: int
    page: int
    pageSize: int
    totalPages: int

class ArticleDetailedOut(ArticleOut):
    fullText: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    sentiment: Optional[str] = None

class CategoryCount(BaseModel):
    category: str
    count: int

class SourceCount(BaseModel):
    source: str
    count: int

class DashboardStats(BaseModel):
    totalArticles: int
    savedArticles: int
    categoryCounts: List[CategoryCount]
    sourceCounts: List[SourceCount]
    recentArticleCount: int  # Articles from last 24h

class SaveArticleRequest(BaseModel):
    saved: bool

# Utility functions
def serialize_article(doc: Dict[str, Any], include_full_text: bool = False) -> Dict[str, Any]:
    """Convert MongoDB document to API response format"""
    article = {
        "id": doc.get("id"),
        "title": doc.get("title"),
        "summary": doc.get("summary"),
        "category": doc.get("category"),
        "source": doc.get("source"),
        "imageUrl": doc.get("imageUrl") or doc.get("image_url", ""),
        "fullArticleUrl": doc.get("fullArticleUrl") or doc.get("url", ""),
        "publishedAt": doc.get("publishedAt") or doc.get("published_at", ""),
        "saved": doc.get("saved", False),
        "viewCount": doc.get("viewCount", 0),
        "readTimeMinutes": doc.get("readTimeMinutes", None)
    }
    
    if include_full_text:
        article["fullText"] = doc.get("full_text", "")
        article["keywords"] = doc.get("keywords", [])
        article["sentiment"] = doc.get("sentiment", None)
        
    return article

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """Verify API key if configured"""
    if not API_KEY:
        return True
    
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return True

# Create custom exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.detail,
            code=exc.status_code,
            details=getattr(exc, "details", None)
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            message="An unexpected error occurred",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(exc)} if app.debug else None
        ).dict()
    )

# API Endpoints
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to docs"""
    return {"message": f"Welcome to {API_TITLE}. Visit /docs for API documentation."}

@app.get("/docs", include_in_schema=False)
async def get_docs():
    """Custom Swagger UI"""
    return get_swagger_ui_html(
        openapi_url=f"{API_PREFIX}/openapi.json",
        title=f"{API_TITLE} - API Documentation"
    )

@app.get(f"{API_PREFIX}/health")
async def health_check(_: bool = Depends(verify_api_key)):
    """Check API health status"""
    try:
        # Check database connection
        db_manager.client.admin.command('ping')
        article_count = articles_collection.count_documents({})
        
        return SuccessResponse(data={
            "status": "healthy",
            "version": API_VERSION,
            "database": "connected",
            "article_count": article_count,
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
            headers={"Retry-After": "60"}
        )

@app.get(
    f"{API_PREFIX}/articles",
    response_model=ArticleList,
    summary="Get paginated articles with optional filtering"
)
async def get_articles(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    source: Optional[str] = Query(None, description="Filter by source"),
    saved_only: Optional[bool] = Query(None, description="Filter saved articles only"),
    sort_by: str = Query("publishedAt", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    _: bool = Depends(verify_api_key)
):
    """
    Get a paginated list of articles with optional filtering and sorting.
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of articles per page
    - **category**: Filter by category name
    - **source**: Filter by source name
    - **saved_only**: If true, return only saved articles
    - **sort_by**: Field to sort by (publishedAt, title, source, category)
    - **sort_order**: Sort direction (asc or desc)
    """
    try:
        # Build query
        query = {}
        if category:
            query["category"] = category
        if source:
            query["source"] = source
        if saved_only is not None:
            query["saved"] = saved_only
        
        # Get total count for pagination
        total_count = articles_collection.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = (total_count + page_size - 1) // page_size
        
        # Validate sort parameters
        valid_sort_fields = ["publishedAt", "title", "source", "category", "viewCount"]
        if sort_by not in valid_sort_fields:
            sort_by = "publishedAt"
            
        sort_direction = -1 if sort_order.lower() == "desc" else 1
        
        # Execute query with pagination
        articles = list(articles_collection.find(
            query,
            {'full_text': 0, 'keywords': 0}  # Exclude large fields
        ).sort(sort_by, sort_direction).skip(skip).limit(page_size))
        
        # Return formatted response
        return ArticleList(
            articles=[serialize_article(a) for a in articles],
            totalCount=total_count,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    except Exception as e:
        logger.error(f"Error in get_articles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch articles"
        )

@app.get(
    f"{API_PREFIX}/articles/search",
    response_model=ArticleList,
    summary="Search articles by text, category or source"
)
async def search_articles(
    q: str = Query("", description="Search text"),
    category: Optional[str] = Query(None, description="Filter by category"),
    source: Optional[str] = Query(None, description="Filter by source"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    _: bool = Depends(verify_api_key)
):
    """
    Search articles by text with optional category and source filters.
    
    - **q**: Search text to find in title or summary
    - **category**: Optional category filter
    - **source**: Optional source filter
    - **page**: Page number (starts at 1) 
    - **page_size**: Number of articles per page
    """
    try:
        # Build search query
        query = {}
        
        # Add text search if provided
        if q:
            query["$text"] = {"$search": q}
        
        # Add filters if provided
        if category:
            query["category"] = category
        if source:
            query["source"] = source
            
        # Get total count
        total_count = articles_collection.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = (total_count + page_size - 1) // page_size
        
        # Execute query with pagination and sort by relevance if text search is used
        cursor = articles_collection.find(
            query,
            {'full_text': 0, 'keywords': 0}  # Exclude large fields
        )
        
        # Sort by text score if text search is used, otherwise by date
        if q:
            cursor = cursor.sort([("score", {"$meta": "textScore"}), ("publishedAt", -1)])
        else:
            cursor = cursor.sort("publishedAt", -1)
            
        articles = list(cursor.skip(skip).limit(page_size))
        
        # Return formatted response
        return ArticleList(
            articles=[serialize_article(a) for a in articles],
            totalCount=total_count,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    except Exception as e:
        logger.error(f"Error in search_articles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@app.get(
    f"{API_PREFIX}/article/{{article_id}}",
    response_model=ArticleDetailedOut,
    summary="Get a single article by ID"
)
async def get_article_by_id(
    article_id: str = Path(..., description="Article ID"),
    increment_view: bool = Query(True, description="Increment view count"),
    _: bool = Depends(verify_api_key)
):
    """
    Get detailed information about a specific article by ID.
    
    - **article_id**: Unique ID of the article
    - **increment_view**: Whether to increment the view count
    """
    try:
        # Find the article
        article = articles_collection.find_one({"id": article_id})
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with ID {article_id} not found"
            )
        
        # Increment view count if requested
        if increment_view:
            articles_collection.update_one(
                {"id": article_id},
                {"$inc": {"viewCount": 1}}
            )
            article["viewCount"] = article.get("viewCount", 0) + 1
            
        # Return detailed article
        return serialize_article(article, include_full_text=True)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_article_by_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch article"
        )

@app.post(
    f"{API_PREFIX}/article/{{article_id}}/save",
    response_model=SuccessResponse,
    summary="Save or unsave an article"
)
async def toggle_saved_status(
    article_id: str = Path(..., description="Article ID"),
    request: SaveArticleRequest = None,
    _: bool = Depends(verify_api_key)
):
    """
    Toggle or set saved status for an article.
    
    - **article_id**: Unique ID of the article
    - **request**: Optional request body with "saved" field to set specific state
    """
    try:
        # Find the article
        article = articles_collection.find_one({"id": article_id})
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article with ID {article_id} not found"
            )
        
        # Determine new saved state
        current_status = article.get("saved", False)
        if request is not None:
            new_status = request.saved
        else:
            new_status = not current_status
        
        # Update the article
        result = articles_collection.update_one(
            {"id": article_id},
            {"$set": {"saved": new_status, "updatedAt": datetime.utcnow().isoformat()}}
        )
        
        if result.modified_count < 1:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update article saved status"
            )
        
        return SuccessResponse(data={
            "id": article_id,
            "saved": new_status
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in toggle_saved_status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update article saved status"
        )

@app.get(
    f"{API_PREFIX}/categories",
    response_model=SuccessResponse,
    summary="Get all available categories"
)
async def get_categories(_: bool = Depends(verify_api_key)):
    """Get a list of all available categories with article counts"""
    try:
        # Get categories with counts using aggregation
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        
        categories = []
        for doc in articles_collection.aggregate(pipeline):
            if doc["_id"]:  # Skip null/empty categories
                categories.append({
                    "name": doc["_id"],
                    "count": doc["count"]
                })
        
        return SuccessResponse(data=categories)
    except Exception as e:
        logger.error(f"Error in get_categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch categories"
        )

@app.get(
    f"{API_PREFIX}/sources",
    response_model=SuccessResponse,
    summary="Get all available sources"
)
async def get_sources(_: bool = Depends(verify_api_key)):
    """Get a list of all available news sources with article counts"""
    try:
        # Get sources with counts using aggregation
        pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        
        sources = []
        for doc in articles_collection.aggregate(pipeline):
            if doc["_id"]:  # Skip null/empty sources
                sources.append({
                    "name": doc["_id"],
                    "count": doc["count"]
                })
        
        return SuccessResponse(data=sources)
    except Exception as e:
        logger.error(f"Error in get_sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch sources"
        )

@app.get(
    f"{API_PREFIX}/dashboard/stats",
    response_model=DashboardStats,
    summary="Get dashboard statistics"
)
async def get_dashboard_stats(_: bool = Depends(verify_api_key)):
    """Get statistics for dashboard overview"""
    try:
        # Get total articles
        total_articles = articles_collection.count_documents({})
        
        # Get saved articles
        saved_articles = articles_collection.count_documents({"saved": True})
        
        # Get recent articles (last 24h)
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        recent_articles = articles_collection.count_documents({"publishedAt": {"$gte": yesterday}})
        
        # Get category counts
        category_pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        category_counts = []
        for doc in articles_collection.aggregate(category_pipeline):
            if doc["_id"]:
                category_counts.append(CategoryCount(
                    category=doc["_id"],
                    count=doc["count"]
                ))
        
        # Get source counts
        source_pipeline = [
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        source_counts = []
        for doc in articles_collection.aggregate(source_pipeline):
            if doc["_id"]:
                source_counts.append(SourceCount(
                    source=doc["_id"],
                    count=doc["count"]
                ))
        
        return DashboardStats(
            totalArticles=total_articles,
            savedArticles=saved_articles,
            categoryCounts=category_counts,
            sourceCounts=source_counts,
            recentArticleCount=recent_articles
        )
    except Exception as e:
        logger.error(f"Error in get_dashboard_stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard statistics"
        )

@app.get(
    f"{API_PREFIX}/articles/trending",
    response_model=List[ArticleOut],
    summary="Get trending articles based on view count"
)
async def get_trending_articles(
    days: int = Query(7, ge=1, le=30, description="Time period in days"),
    limit: int = Query(5, ge=1, le=20, description="Number of articles to return"),
    _: bool = Depends(verify_api_key)
):
    """
    Get trending articles based on view count from the specified time period.
    
    - **days**: Number of days to look back (1-30)
    - **limit**: Number of trending articles to return (1-20)
    """
    try:
        # Calculate the date threshold
        threshold_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Find trending articles
        articles = list(articles_collection.find({
            "publishedAt": {"$gte": threshold_date}
        }).sort("viewCount", -1).limit(limit))
        
        return [serialize_article(a) for a in articles]
    except Exception as e:
        logger.error(f"Error in get_trending_articles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch trending articles"
        )

@app.get(
    f"{API_PREFIX}/articles/latest",
    response_model=List[ArticleOut],
    summary="Get latest articles"
)
async def get_latest_articles(
    limit: int = Query(30, ge=1, le=100, description="Number of articles to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    source: Optional[str] = Query(None, description="Filter by source"),
    _: bool = Depends(verify_api_key)
):
    """
    Get the latest articles, optionally filtered by category or source.
    
    - **limit**: Number of articles to return (1-100)
    - **category**: Optional category filter
    - **source**: Optional source filter
    """
    try:
        # Build query
        query = {}
        if category:
            query["category"] = category
        if source:
            query["source"] = source
        
        # Find latest articles
        articles = list(articles_collection.find(
            query,
            {'full_text': 0, 'keywords': 0}  # Exclude large fields
        ).sort("publishedAt", -1).limit(limit))
        
        return [serialize_article(a) for a in articles]
    except Exception as e:
        logger.error(f"Error in get_latest_articles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch latest articles"
        )

# Entry point for running the API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app", 
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "development") == "development"
    )