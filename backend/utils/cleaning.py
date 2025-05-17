import re
from datetime import datetime
from bs4 import BeautifulSoup

def clean_html(raw_html: str) -> str:
    """
    Remove all HTML tags and scripts/styles from raw HTML content.
    """
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    text = soup.get_text(separator=" ")

    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_text(text: str) -> str:
    """
    Additional text cleanup: remove unwanted characters.
    """
    if not text:
        return ""

    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E]+', ' ', text)

    # Normalize spaces again
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def parse_datetime(date_str: str):
    """
    Try to parse a date string into a datetime object.
    Supports ISO8601 and common formats.
    """
    if not date_str:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    return None

def validate_article(article: dict) -> bool:
    """
    Ensure required fields exist and are not empty.
    """
    required = ["title", "url", "content", "published_at"]
    for field in required:
        if not article.get(field):
            return False
    return True
