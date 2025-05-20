"""
Enhanced web scraper for news articles
Includes source-specific extraction, proper user-agent, rate limiting, and better error handling
"""
import time
import random
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("scraper")

# Set a proper user agent to respect website policies
HEADERS = {
    "User-Agent": "Mozilla/5.0 NewsAggregator/1.0 (Educational Project; contact@example.com)",
    "Accept": "text/html,application/xhtml+xml,application/xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# Define news sources with their RSS/archive URLs
SOURCES = {
    "Reuters": "https://www.reuters.com/news/archive/worldNews",
    "NPR": "https://www.npr.org/sections/news/",
    "The Guardian": "https://www.theguardian.com/international",
    "AP News": "https://apnews.com/hub/world-news",
    "BBC": "https://www.bbc.com/news/world",
    "Al Jazeera": "https://www.aljazeera.com/news/",
}

# Source-specific article link patterns to validate URLs
URL_PATTERNS = {
    "Reuters": "reuters.com/",
    "NPR": "npr.org/",
    "The Guardian": "theguardian.com/",
    "AP News": "apnews.com/article/",
    "BBC": "bbc.com/news/",
    "Al Jazeera": "aljazeera.com/news/",
}

def make_request(url: str, timeout: int = 15) -> Optional[str]:
    """Make an HTTP request with proper error handling and rate limiting."""
    try:
        # Add small delay for politeness
        time.sleep(random.uniform(1, 3))
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None

def extract_article_links_reuters(html: str) -> List[str]:
    """Extract article links from Reuters."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for article in soup.select("article.story"):
        link_elem = article.select_one("a.story-content")
        if link_elem and link_elem.get("href"):
            href = link_elem["href"]
            # Handle relative URLs
            if href.startswith("/"):
                href = f"https://www.reuters.com{href}"
            if "reuters.com" in href:
                links.add(href)
    return list(links)

def extract_article_links_guardian(html: str) -> List[str]:
    """Extract article links from The Guardian."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    # Look for headline links
    for tag in soup.select("a.js-headline-text"):
        href = tag.get("href")
        if href:
            # Handle relative URLs
            if href.startswith("/"):
                href = f"https://www.theguardian.com{href}"
            if "theguardian.com" in href:
                links.add(href)
    return list(links)

def extract_article_links_ap(html: str) -> List[str]:
    """Extract article links from AP News."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for link in soup.select('a[href^="https://apnews.com/article/"]'):
        links.add(link['href'])
    return list(links)

def extract_article_links_bbc(html: str) -> List[str]:
    """Extract article links from BBC."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for link in soup.select('a.gs-c-promo-heading'):
        href = link.get('href')
        if href:
            # Handle relative URLs
            if href.startswith('/'):
                href = f"https://www.bbc.com{href}"
            if "bbc.com/news" in href:
                links.add(href)
    return list(links)

def extract_article_links_npr(html: str) -> List[str]:
    """Extract article links from NPR."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for link in soup.select('h2.title a'):
        href = link.get('href')
        if href and "npr.org" in href:
            links.add(href)
    return list(links)

def extract_article_links_aljazeera(html: str) -> List[str]:
    """Extract article links from Al Jazeera."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for link in soup.select('article a'):
        href = link.get('href')
        if href:
            # Handle relative URLs
            if href.startswith('/'):
                href = f"https://www.aljazeera.com{href}"
            if "aljazeera.com/news" in href:
                links.add(href)
    return list(links)

def get_article_links(source: str, url: str) -> List[str]:
    """Get article links from a news source."""
    html = make_request(url)
    if not html:
        logger.warning(f"Failed to fetch content from {source}: {url}")
        return []
    
    # Source-specific extraction
    if source == "Reuters":
        links = extract_article_links_reuters(html)
    elif source == "The Guardian":
        links = extract_article_links_guardian(html)
    elif source == "AP News":
        links = extract_article_links_ap(html)
    elif source == "BBC":
        links = extract_article_links_bbc(html)
    elif source == "NPR":
        links = extract_article_links_npr(html)
    elif source == "Al Jazeera":
        links = extract_article_links_aljazeera(html)
    else:
        # Generic fallback extraction
        soup = BeautifulSoup(html, "html.parser")
        links = [a['href'] for a in soup.find_all("a", href=True) 
                if a["href"].startswith("http") and URL_PATTERNS.get(source, "") in a["href"]]
    
    # Filter out duplicates and limit to top results
    unique_links = list(set(links))
    logger.info(f"Found {len(unique_links)} links from {source}")
    return unique_links[:20]  # Limit to top 20 articles per source

def detect_article_category(title: str, text: str) -> str:
    """Detect article category based on content."""
    # Simple keyword-based categorization
    categories = {
        "politics": ["government", "election", "president", "minister", "parliament", "vote", "political"],
        "technology": ["tech", "computer", "software", "internet", "digital", "ai", "artificial intelligence"],
        "business": ["economy", "market", "stock", "trade", "company", "financial", "investment"],
        "health": ["covid", "virus", "disease", "medical", "hospital", "doctor", "healthcare", "health"],
        "entertainment": ["movie", "film", "music", "celebrity", "actor", "actress", "concert"],
        "sports": ["football", "soccer", "basketball", "tournament", "championship", "olympic", "player"],
        "science": ["research", "scientist", "study", "discovery", "space", "nasa", "physics", "biology"],
        "environment": ["climate", "pollution", "environmental", "green", "sustainability", "conservation"]
    }
    
    content = (title + " " + text).lower()
    
    for category, keywords in categories.items():
        if any(keyword in content for keyword in keywords):
            return category
    
    return "general"

def scrape_article(url: str) -> Optional[Dict]:
    """Scrape article content from URL with enhanced error handling."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()  # Extract keywords and summary
        
        # Validate article
        if not article.title or not article.text or len(article.text) < 300:
            logger.warning(f"Invalid article content for {url}")
            return None
            
        category = detect_article_category(article.title, article.text)
        
        return {
            "title": article.title,
            "text": article.text,
            "url": url,
            "image_url": article.top_image or "",
            "published_at": article.publish_date.isoformat() if article.publish_date else datetime.utcnow().isoformat(),
            "keywords": article.keywords,
            "category": category,
            "source_summary": article.summary  # Newspaper's built-in summary as backup
        }
    except ArticleException as e:
        logger.error(f"ArticleException for {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to scrape article {url}: {e}")
        return None


if __name__ == "__main__":
    # Test the scraper for a specific source
    source_name = "BBC"
    print(f"Testing scraper for {source_name}")
    links = get_article_links(source_name, SOURCES[source_name])
    print(f"Found {len(links)} links")
    if links:
        article_data = scrape_article(links[0])
        if article_data:
            print(f"Successfully scraped: {article_data['title']}")
            print(f"Category: {article_data['category']}")
            print(f"Image URL: {article_data['image_url']}")