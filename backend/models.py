from uuid import uuid4
from datetime import datetime

def create_article_dict(title, summary, full_text, url, image_url, source, published_at, category=None):
    return {
        "id": str(uuid4()),
        "title": title,
        "summary": summary,
        "full_text": full_text,
        "fullArticleUrl": url,
        "imageUrl": image_url,
        "source": source,
        "category": category or "general",
        "publishedAt": published_at,
        "createdAt": datetime.utcnow().isoformat(),
        "saved": False
    }
