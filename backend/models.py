"""
Enhanced data models for the news aggregation system
"""
from uuid import uuid4
from datetime import datetime
from typing import Dict, Any, Optional, List

def create_article_dict(
    title: str, 
    summary: str, 
    full_text: str, 
    url: str, 
    image_url: Optional[str] = None,
    source: str = "",
    published_at: Optional[str] = None,
    category: str = "general",
    keywords: Optional[List[str]] = None,
    sentiment: Optional[str] = None,
    read_time: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a standardized article dictionary with enhanced metadata.
    
    Args:
        title: Article title
        summary: Article summary
        full_text: Full article text
        url: URL of the original article
        image_url: URL of the article's main image
        source: Source name (e.g., "Reuters", "NPR")
        published_at: ISO format datetime when article was published
        category: Article category
        keywords: List of keywords related to the article
        sentiment: Article sentiment analysis
        read_time: Estimated reading time in minutes
        
    Returns:
        Dictionary with article data
    """
    # Calculate reading time if not provided
    if read_time is None and full_text:
        # Average reading speed is around 200-250 words per minute
        word_count = len(full_text.split())
        read_time = max(1, round(word_count / 200))
    
    # Generate article ID based on URL to avoid duplicates
    unique_id = str(uuid4())
    
    # Use current time if published date is not available
    if not published_at:
        published_at = datetime.utcnow().isoformat()
    
    # Normalize category
    if not category or category.lower() == "none":
        category = "general"
    
    # Create keywords list if none provided
    if not keywords:
        keywords = []
    
    return {
        "id": unique_id,
        "title": title,
        "summary": summary,
        "full_text": full_text,
        "fullArticleUrl": url,
        "imageUrl": image_url or "",
        "source": source,
        "category": category.lower(),
        "publishedAt": published_at,
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "keywords": keywords,
        "sentiment": sentiment,
        "readTimeMinutes": read_time,
        "wordCount": len(full_text.split()) if full_text else 0,
        "saved": False,
        "viewCount": 0,
        "hasImage": bool(image_url)
    }

def extract_article_metadata(article_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from an article for analytics purposes.
    
    Args:
        article_dict: Complete article dictionary
        
    Returns:
        Dictionary with article metadata
    """
    return {
        "id": article_dict["id"],
        "title": article_dict["title"],
        "source": article_dict["source"],
        "category": article_dict["category"],
        "publishedAt": article_dict["publishedAt"],
        "createdAt": article_dict["createdAt"],
        "wordCount": article_dict["wordCount"],
        "hasImage": article_dict["hasImage"],
        "readTimeMinutes": article_dict.get("readTimeMinutes", 0)
    }