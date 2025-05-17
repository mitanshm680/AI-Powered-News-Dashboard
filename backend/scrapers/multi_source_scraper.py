from __future__ import annotations
import random
import time
import requests
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from backend.db.mongo import upsert_articles
from backend.utils.cleaning import clean_html, clean_text, parse_datetime, validate_article
from backend.utils.logger import log

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
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
        upsert_articles(articles)
        return articles

    def _get(self, url: str) -> BeautifulSoup:
        time.sleep(random.uniform(self.delay_min, self.delay_max))
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            res.raise_for_status()
            return BeautifulSoup(res.text, "html.parser")
        except Exception as e:
            log.warning(f"Request failed for {url}: {e}")
            raise

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _build_article(self, *, title: str, url: str, raw_content: str, published_at_raw: str, source: str) -> dict | None:
        content = clean_text(clean_html(raw_content))
        dt_obj = parse_datetime(published_at_raw)
        published_at = dt_obj.isoformat() if dt_obj else self._now()
        article = {
            "title": title,
            "url": url,
            "published_at": published_at,
            "content": content,
            "source": source,
        }
        if validate_article(article):
            return article
        log.warning(f"Skipping invalid {source} article: {url}")
        return None

    # === Reuters ===
    def _scrape_reuters(self) -> list[dict]:
        soup = self._get("https://www.reuters.com/world/")
        links = {
            urljoin("https://www.reuters.com", a["href"].split("?")[0])
            for a in soup.select("a[data-testid='Heading']") if a.get("href")
        }
        return [a for url in list(links)[:10] if (a := self._parse_reuters(url))]

    def _parse_reuters(self, url: str) -> dict | None:
        try:
            soup = self._get(url)
            title_tag = soup.find("h1")
            content_blocks = soup.select("article p")
            dt = soup.find("time")
            if not title_tag or not content_blocks:
                return None
            title = title_tag.get_text(strip=True)
            content = "\n".join(p.get_text(" ", strip=True) for p in content_blocks)
            return self._build_article(
                title=title, url=url, raw_content=content,
                published_at_raw=dt["datetime"] if dt and dt.has_attr("datetime") else self._now(), source="Reuters"
            )
        except Exception as e:
            log.warning(f"Reuters parsing failed: {url} | {e}")
            return None

    # === AP News ===
    def _scrape_apnews(self) -> list[dict]:
        soup = self._get("https://apnews.com/hub/world-news")
        links = {
            urljoin("https://apnews.com", a["href"])
            for a in soup.select("a.Link") if "/article/" in a.get("href", "")
        }
        return [a for url in list(links)[:10] if (a := self._parse_apnews(url))]

    def _parse_apnews(self, url: str) -> dict | None:
        try:
            soup = self._get(url)
            title_tag = soup.find("h1")
            content_blocks = soup.select("div.Article p")
            dt = soup.find("time")
            if not title_tag or not content_blocks:
                return None
            title = title_tag.get_text(strip=True)
            content = "\n".join(p.get_text(" ", strip=True) for p in content_blocks)
            return self._build_article(
                title=title, url=url, raw_content=content,
                published_at_raw=dt["datetime"] if dt and dt.has_attr("datetime") else self._now(), source="AP News"
            )
        except Exception as e:
            log.warning(f"AP parsing failed: {url} | {e}")
            return None

    # === NPR ===
    def _scrape_npr(self) -> list[dict]:
        soup = self._get("https://www.npr.org/sections/world/")
        links = {
            a["href"] for a in soup.select("article a[href]") if a["href"].startswith("https://www.npr.org/")
        }
        return [a for url in list(links)[:10] if (a := self._parse_npr(url))]

    def _parse_npr(self, url: str) -> dict | None:
        try:
            soup = self._get(url)
            title_tag = soup.find("h1")
            content_blocks = soup.select("div[data-testid='storytext'] p")
            dt = soup.find("time")
            if not title_tag or not content_blocks:
                return None
            title = title_tag.get_text(strip=True)
            content = "\n".join(p.get_text(" ", strip=True) for p in content_blocks)
            return self._build_article(
                title=title, url=url, raw_content=content,
                published_at_raw=dt["datetime"] if dt and dt.has_attr("datetime") else self._now(), source="NPR"
            )
        except Exception as e:
            log.warning(f"NPR parsing failed: {url} | {e}")
            return None

    # === The Guardian ===
    def _scrape_guardian(self) -> list[dict]:
        soup = self._get("https://www.theguardian.com/world")
        links = {
            a["href"] for a in soup.select("a.js-headline-text[href]") if a["href"].startswith("https://")
        }
        return [a for url in list(links)[:10] if (a := self._parse_guardian(url))]

    def _parse_guardian(self, url: str) -> dict | None:
        try:
            soup = self._get(url)
            title_tag = soup.find("h1")
            content_blocks = soup.select("div.article-body-commercial-selector p")
            dt = soup.find("time")
            if not title_tag or not content_blocks:
                return None
            title = title_tag.get_text(strip=True)
            content = "\n".join(p.get_text(" ", strip=True) for p in content_blocks)
            dt_attr = dt["datetime"] if dt and dt.has_attr("datetime") else self._now()
            return self._build_article(
                title=title, url=url, raw_content=content,
                published_at_raw=dt_attr, source="The Guardian"
            )
        except Exception as e:
            log.warning(f"Guardian parsing failed: {url} | {e}")
            return None
