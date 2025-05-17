from __future__ import annotations
import random
import time
import requests
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from backend.utils.cleaning import clean_html, clean_text, parse_datetime, validate_article
from backend.utils.logger import log


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


class MultiSourceScraper:
    def __init__(self, delay_range: tuple[float, float] = (1.5, 3.0)):
        self.delay_min, self.delay_max = delay_range
        self.sources = {
            "Reuters": self._scrape_reuters,
            "AP News": self._scrape_apnews,
            "NPR": self._scrape_npr,
            "The Guardian": self._scrape_guardian,
        }

    def scrape(self) -> list[dict]:
        articles = []
        for name, scraper_func in self.sources.items():
            try:
                batch = scraper_func()
                articles.extend(batch)
                log.info(f"✅ {name}: {len(batch)} articles scraped")
            except Exception as e:
                log.error(f"❌ {name} scraper failed: {e}")
        return articles

    def _get(self, url: str) -> BeautifulSoup:
        time.sleep(random.uniform(self.delay_min, self.delay_max))
        res = requests.get(url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        return BeautifulSoup(res.text, "html.parser")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # Reuters
    def _scrape_reuters(self) -> list[dict]:
        start_url = "https://www.reuters.com/world/"
        soup = self._get(start_url)
        links = {
            urljoin("https://www.reuters.com", a["href"].split("?")[0])
            for a in soup.select("a[data-testid='Heading']")
        }
        articles = []
        for url in list(links)[:10]:
            article = self._parse_reuters(url)
            if article:
                articles.append(article)
        return articles

    def _parse_reuters(self, url: str) -> dict | None:
        soup = self._get(url)
        title = soup.find("h1").get_text(strip=True)
        raw_content = "\n".join(p.get_text(" ", strip=True) for p in soup.select("article p"))
        dt = soup.find("time")
        published_at_raw = dt["datetime"] if dt else self._now()

        # Clean content
        content = clean_html(raw_content)
        content = clean_text(content)

        # Parse and normalize publish date
        dt_obj = parse_datetime(published_at_raw)
        published_at = dt_obj.isoformat() if dt_obj else self._now()

        article = {
            "title": title,
            "url": url,
            "published_at": published_at,
            "content": content,
            "source": "Reuters",
        }

        if validate_article(article):
            return article
        else:
            log.warning(f"Skipping invalid Reuters article: {url}")
            return None

    # AP News
    def _scrape_apnews(self) -> list[dict]:
        soup = self._get("https://apnews.com/hub/world-news")
        links = {
            urljoin("https://apnews.com", a["href"])
            for a in soup.select("a.Link")
            if "/article/" in a["href"]
        }
        articles = []
        for url in list(links)[:10]:
            article = self._parse_apnews(url)
            if article:
                articles.append(article)
        return articles

    def _parse_apnews(self, url: str) -> dict | None:
        soup = self._get(url)
        title = soup.find("h1").get_text(strip=True)
        raw_content = "\n".join(p.get_text(" ", strip=True) for p in soup.select("div.Article p"))
        dt = soup.find("time")
        published_at_raw = dt["datetime"] if dt else self._now()

        content = clean_html(raw_content)
        content = clean_text(content)

        dt_obj = parse_datetime(published_at_raw)
        published_at = dt_obj.isoformat() if dt_obj else self._now()

        article = {
            "title": title,
            "url": url,
            "published_at": published_at,
            "content": content,
            "source": "AP News",
        }

        if validate_article(article):
            return article
        else:
            log.warning(f"Skipping invalid AP News article: {url}")
            return None

    # NPR
    def _scrape_npr(self) -> list[dict]:
        soup = self._get("https://www.npr.org/sections/world/")
        links = {
            a["href"] for a in soup.select("article a")
            if a["href"].startswith("https://www.npr.org/")
        }
        articles = []
        for url in list(links)[:10]:
            article = self._parse_npr(url)
            if article:
                articles.append(article)
        return articles

    def _parse_npr(self, url: str) -> dict | None:
        soup = self._get(url)
        title = soup.find("h1").get_text(strip=True)
        raw_content = "\n".join(
            p.get_text(" ", strip=True) for p in soup.select("div[data-testid='storytext'] p")
        )
        dt = soup.find("time")
        published_at_raw = dt["datetime"] if dt else self._now()

        content = clean_html(raw_content)
        content = clean_text(content)

        dt_obj = parse_datetime(published_at_raw)
        published_at = dt_obj.isoformat() if dt_obj else self._now()

        article = {
            "title": title,
            "url": url,
            "published_at": published_at,
            "content": content,
            "source": "NPR",
        }

        if validate_article(article):
            return article
        else:
            log.warning(f"Skipping invalid NPR article: {url}")
            return None

    # The Guardian
    def _scrape_guardian(self) -> list[dict]:
        soup = self._get("https://www.theguardian.com/world")
        links = {
            a["href"] for a in soup.select("a.js-headline-text") if a["href"].startswith("https://")
        }
        articles = []
        for url in list(links)[:10]:
            article = self._parse_guardian(url)
            if article:
                articles.append(article)
        return articles

    def _parse_guardian(self, url: str) -> dict | None:
        soup = self._get(url)
        title = soup.find("h1").get_text(strip=True)
        raw_content = "\n".join(
            p.get_text(" ", strip=True) for p in soup.select("div.article-body-commercial-selector p")
        )
        dt = soup.find("time")
        published_at_raw = dt["datetime"] if dt and dt.has_attr("datetime") else self._now()

        content = clean_html(raw_content)
        content = clean_text(content)

        dt_obj = parse_datetime(published_at_raw)
        published_at = dt_obj.isoformat() if dt_obj else self._now()

        article = {
            "title": title,
            "url": url,
            "published_at": published_at,
            "content": content,
            "source": "The Guardian",
        }

        if validate_article(article):
            return article
        else:
            log.warning(f"Skipping invalid The Guardian article: {url}")
            return None
