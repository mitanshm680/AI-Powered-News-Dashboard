import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

HEADERS = {
    "Content-Type": "application/json"
}

def summarize_text(article_text, source=""):
    if not article_text:
        return "No content available to summarize."

    prompt = f"Summarize the following article in 3-4 sentences:\n\n{article_text}\n\nInclude the source name ({source}) at the end."

    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=data,
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        candidates = response.json().get("candidates")
        if candidates:
            return candidates[0]["content"]["parts"][0]["text"]
        return "Summary not available."
    except Exception as e:
        print(f"[ERROR] Summarization failed: {e}")
        return article_text[:300] + "..."  # Fallback summary
