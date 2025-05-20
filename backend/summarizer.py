"""
Enhanced text summarization module using Google's Gemini API
"""
import os
import requests
import time
from typing import Optional
from dotenv import load_dotenv
import logging
from newspaper import fulltext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("summarizer")

load_dotenv()

# API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Default to empty string if not found

# Endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def summarize_with_gemini(text: str, source: str = "", category: str = "general") -> Optional[str]:
    """Summarize text using Google's Gemini API."""
    if not GEMINI_API_KEY:
        logger.warning("Gemini API key not found")
        return None
        
    prompt = f"""
    Summarize the following {category} news article in 3-4 concise sentences that capture the key points.
    
    Source: {source}
    
    Article:
    {text[:8000]}  # Limit text to prevent excessive tokens
    
    Summary:
    """
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 250
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=data,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        candidates = result.get("candidates", [])
        if candidates and candidates[0].get("content", {}).get("parts", []):
            summary = candidates[0]["content"]["parts"][0]["text"]
            return summary.strip()
        else:
            logger.warning("No summary content in Gemini response")
            return None
    except requests.RequestException as e:
        logger.error(f"Gemini API request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Error in Gemini summarization: {e}")
        return None

def simple_text_fallback(text: str, source: str = "") -> str:
    """Create a simple fallback summary without using NLP libraries."""
    try:
        # Split text into sentences (very basic approach)
        sentences = []
        for sent in text.replace("\n", " ").split(". "):
            if sent.strip():
                sentences.append(sent.strip() + ("." if not sent.endswith(".") else ""))
        
        if not sentences:
            return text[:300] + "..."
            
        # Simple extractive summary - first 3 sentences
        summary_sentences = sentences[:min(3, len(sentences))]
        summary = " ".join(summary_sentences)
        
        # Add source attribution
        if source:
            summary += f" (Source: {source})"
            
        return summary
    except Exception as e:
        logger.error(f"Fallback summarization failed: {e}")
        return text[:300] + "..."  # Absolute fallback

def summarize_text(article_text: str, source: str = "", category: str = "general", 
                  max_retries: int = 2, use_fallback: bool = True) -> str:
    """
    Main summarization function with simple fallback and retry logic.
    
    Args:
        article_text: The text to summarize
        source: The source of the article
        category: Article category for context-aware summarization
        max_retries: Maximum number of retries for API calls
        use_fallback: Whether to use fallback summarization
        
    Returns:
        A summary of the article
    """
    if not article_text:
        return "No content available to summarize."
    
    # Try Gemini API with retries
    for attempt in range(max_retries):
        summary = summarize_with_gemini(article_text, source, category)
        if summary:
            return summary
        logger.info(f"Gemini API attempt {attempt+1} failed, retrying...")
        time.sleep(1)  # Wait before retry
    
    # If Gemini API fails, use simple fallback
    if use_fallback:
        logger.info("Using simple fallback summarization")
        return simple_text_fallback(article_text, source)
    
    # Final fallback
    return article_text[:300] + f"... (Source: {source})"


if __name__ == "__main__":
    # Test the summarizer
    test_text = """
    Climate scientists warn that the world is on track to exceed the 1.5°C warming threshold within the next five years.
    A new report from the World Meteorological Organization says there's a 66% chance of temporarily exceeding the threshold between now and 2028.
    The report highlights that greenhouse gas emissions continue to rise despite international agreements to reduce them.
    Scientists say exceeding 1.5°C of warming could trigger irreversible climate tipping points.
    Countries are urged to accelerate their transition to renewable energy sources and implement more aggressive carbon reduction strategies.
    The findings will be central to discussions at the upcoming UN Climate Change Conference.
    """
    
    summary = summarize_text(test_text, source="Test Source", category="environment")
    print("Summary:")
    print(summary)