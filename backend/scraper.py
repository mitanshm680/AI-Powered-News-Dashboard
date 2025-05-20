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

import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("scraper")

# Set a proper user agent to respect website policies and avoid blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}

# Define news sources with their RSS/archive URLs
SOURCES = {
    "Reuters": "https://www.reuters.com/news/archive/worldNews",
    "NPR": "https://www.npr.org/sections/news/",
    "The Guardian": "https://www.theguardian.com/world",
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
        
        # Log status for debugging
        logger.info(f"Request to {url}: Status code {response.status_code}")
        
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None

def extract_article_links_reuters(html: str) -> List[str]:
    """Extract article links from Reuters (updated for 2024 structure)."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    
    # Updated selectors for current Reuters layout
    for article in soup.select("a[data-testid='Heading']"):  # Headings are now in anchor tags
        href = article.get("href")
        if href:
            # Handle relative URLs
            if href.startswith("/"):
                href = f"https://www.reuters.com{href}"
            if "reuters.com/world/" in href:  # Focus on world news links
                links.add(href)
    
    # Additional fallback for story elements
    for story in soup.select("div[data-testid='Story'] a"):
        href = story.get("href")
        if href and "/world/" in href:
            if href.startswith("/"):
                href = f"https://www.reuters.com{href}"
            links.add(href)
    
    logger.info(f"Reuters extraction found {len(links)} links")
    return list(links)

def extract_article_links_guardian(html: str) -> List[str]:
    """Extract article links from The Guardian."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    
    # The Guardian has multiple article card styles
    selectors = [
        "a.js-headline-text", 
        "a[data-link-name='article']",
        ".fc-item__container a",
        ".fc-item__link",
        ".fc-item__content a"
    ]
    
    for selector in selectors:
        for tag in soup.select(selector):
            href = tag.get("href")
            if href:
                # Handle relative URLs
                if href.startswith("/"):
                    href = f"https://www.theguardian.com{href}"
                if "theguardian.com" in href:
                    links.add(href)
    
    logger.info(f"Guardian extraction found {len(links)} links")
    return list(links)

def extract_article_links_ap(html: str) -> List[str]:
    """Extract article links from AP News."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    
    # AP News card structure
    selectors = [
        'a[href^="https://apnews.com/article/"]',
        'a[data-key="card-headline"]',
        '.CardHeadline a',
        'div[data-tb-region="Top Headlines"] a'
    ]
    
    for selector in selectors:
        for link in soup.select(selector):
            href = link.get('href')
            if href and "apnews.com/article" in href:
                links.add(href)
    
    logger.info(f"AP News extraction found {len(links)} links")
    return list(links)

def extract_article_links_bbc(html: str) -> List[str]:
    """Extract article links from BBC."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    
    # BBC selectors
    selectors = [
        'a.gs-c-promo-heading',
        'a.media__link',
        '.nw-o-link-split__anchor',
        '.gs-c-promo .gs-c-promo-heading a'
    ]
    
    for selector in selectors:
        for link in soup.select(selector):
            href = link.get('href')
            if href:
                # Handle relative URLs
                if href.startswith('/'):
                    href = f"https://www.bbc.com{href}"
                if "bbc.com/news" in href or "bbc.co.uk/news" in href:
                    links.add(href)
    
    logger.info(f"BBC extraction found {len(links)} links")
    return list(links)

def extract_article_links_npr(html: str) -> List[str]:
    """Extract article links from NPR."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    
    # NPR selectors
    selectors = [
        'h2.title a',
        '.item-info a',
        '.story-wrap a',
        '.title a',
        'h3.title a',
        'div.story-text a',
        'article a.title'
    ]
    
    for selector in selectors:
        for link in soup.select(selector):
            href = link.get('href')
            if href and "npr.org" in href:
                links.add(href)
    
    logger.info(f"NPR extraction found {len(links)} links")
    return list(links)

def extract_article_links_aljazeera(html: str) -> List[str]:
    """Extract article links from Al Jazeera."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    
    # Al Jazeera selectors
    selectors = [
        'article a',
        '.gc__title a',
        '.gc__header-wrap a',
        '.article-card a',
        '.featured-articles-list a'
    ]
    
    for selector in selectors:
        for link in soup.select(selector):
            href = link.get('href')
            if href:
                # Handle relative URLs
                if href.startswith('/'):
                    href = f"https://www.aljazeera.com{href}"
                if "aljazeera.com/news" in href or "aljazeera.com/features" in href:
                    links.add(href)
    
    logger.info(f"Al Jazeera extraction found {len(links)} links")
    return list(links)

def extract_generic_article_links(html: str, source_pattern: str) -> List[str]:
    """Generic article link extraction for any news source."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    
    # Look for common article link patterns
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href and source_pattern in href and (link.text.strip() or link.find('img')):
            # Filter out navigation, footer, etc. by requiring text content
            if len(link.text.strip()) > 15 or link.find('img'):
                # Handle relative URLs
                if href.startswith('/'):
                    domain = source_pattern.replace('/', '')
                    if '.' in domain:
                        href = f"https://www.{domain}{href}"
                    else:
                        # Can't determine domain from pattern
                        continue
                links.add(href)
    
    return list(links)

def get_article_links(source: str, url: str) -> List[str]:
    """Get article links from a news source."""
    html = make_request(url)
    if not html:
        logger.warning(f"Failed to fetch content from {source}: {url}")
        return []
    
    # Source-specific extraction
    source_extractors = {
        "Reuters": extract_article_links_reuters,
        "The Guardian": extract_article_links_guardian,
        "AP News": extract_article_links_ap,
        "BBC": extract_article_links_bbc,
        "NPR": extract_article_links_npr,
        "Al Jazeera": extract_article_links_aljazeera
    }
    
    # Try source-specific extraction
    if source in source_extractors:
        links = source_extractors[source](html)
    else:
        # Generic fallback extraction
        source_pattern = URL_PATTERNS.get(source, source.lower())
        links = extract_generic_article_links(html, source_pattern)
    
    # If no links found with specific extractor, try generic approach
    if not links and source in URL_PATTERNS:
        logger.warning(f"No links found with specific extractor for {source}, trying generic approach")
        links = extract_generic_article_links(html, URL_PATTERNS[source])
    
    # Filter out duplicates and limit to top results
    unique_links = list(set(links))
    logger.info(f"Found {len(unique_links)} links from {source}")
    
    # Return top 20 articles per source
    result = unique_links[:min(20, len(unique_links))]
    
    # Debug: print first few links to check
    if result:
        logger.info(f"First article link: {result[0]}")
    
    return result

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
        # Set user agent to avoid blocking
        article.config.browser_user_agent = HEADERS["User-Agent"]
        article.download()
        article.parse()
        
        # Try to run NLP, but don't fail if it doesn't work
        try:
            article.nlp()  # Extract keywords and summary
        except Exception as nlp_error:
            logger.warning(f"NLP processing failed for {url}: {nlp_error}")
            # Continue without NLP results
        
        # Validate article
        if not article.title or not article.text or len(article.text) < 100:
            logger.warning(f"Invalid article content for {url}: Title exists: {bool(article.title)}, Text length: {len(article.text) if article.text else 0}")
            return None
            
        category = detect_article_category(article.title, article.text)
        
        # Get keywords if NLP worked, otherwise empty list
        keywords = article.keywords if hasattr(article, 'keywords') and article.keywords else []
        
        return {
            "title": article.title,
            "text": article.text,
            "url": url,
            "image_url": article.top_image or "",
            "published_at": article.publish_date.isoformat() if article.publish_date else datetime.utcnow().isoformat(),
            "keywords": keywords,
            "category": category,
            "source_summary": article.summary if hasattr(article, 'summary') else ""  # Newspaper's built-in summary as backup
        }
    except ArticleException as e:
        logger.error(f"ArticleException for {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to scrape article {url}: {e}")
        return None


if __name__ == "__main__":
    # Test the scraper with verbose output for each source
    for source_name, source_url in SOURCES.items():
        print(f"\nTesting scraper for {source_name}")
        links = get_article_links(source_name, source_url)
        print(f"Found {len(links)} links")
        
        if links:
            print(f"First 3 links:")
            for i, link in enumerate(links[:3]):
                print(f"{i+1}. {link}")
                
            print("\nTesting article scraping for first link...")
            article_data = scrape_article(links[0])
            
            if article_data:
                print(f"Successfully scraped: {article_data['title']}")
                print(f"Category: {article_data['category']}")
                print(f"Image URL: {article_data['image_url']}")
                print(f"Summary length: {len(article_data.get('source_summary', ''))}")
            else:
                print(f"Failed to scrape article from {links[0]}")
        
        print("-" * 50)