from newspaper import Article
from datetime import datetime
import requests
from bs4 import BeautifulSoup

SOURCES = {
    "Reuters": "https://www.reuters.com/news/archive/worldNews",
    "NPR": "https://www.npr.org/sections/news/",
    "The Guardian": "https://www.theguardian.com/international",
    "AP News": "https://apnews.com/hub/world-news"
}

def extract_article_links_guardian(html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.select("a.js-headline-text"):
        href = tag.get("href")
        if href and href.startswith("https://"):
            links.add(href)
    return list(links)

def extract_article_links_ap(html):
    soup = BeautifulSoup(html, "html.parser")
    return [a['href'] for a in soup.select('a[href^="https://apnews.com/article/"]')]

def get_article_links(source, url):
    try:
        response = requests.get(url, timeout=15)
        if source == "The Guardian":
            return extract_article_links_guardian(response.text)
        elif source == "AP News":
            return extract_article_links_ap(response.text)
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            return list(set(a['href'] for a in soup.find_all("a", href=True) if a["href"].startswith("https://")))
    except Exception as e:
        print(f"[ERROR] Failed to get links from {source}: {e}")
        return []

def scrape_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()

        return {
            "title": article.title,
            "text": article.text,
            "url": url,
            "image_url": article.top_image or "",
            "published_at": article.publish_date.isoformat() if article.publish_date else datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"[ERROR] Failed to scrape article: {url} | {e}")
        return None
