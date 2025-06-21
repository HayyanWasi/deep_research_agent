
from newspaper import Article
from bs4 import BeautifulSoup
import requests
from typing import Dict

def smart_scrape_url(url: str) -> Dict:
    """Scrape logic with better error handling"""
    print(f"🔎 Scraping: {url}")
    
    # --- First attempt: newspaper3k ---
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.text and len(article.text) > 100:
            return {
                "title": article.title or "No Title",
                "text": article.text,
                "method": "newspaper3k"
            }
    except Exception as e:
        print(f"❌ newspaper3k failed for {url}:", str(e))

    # --- Fallback: BeautifulSoup ---
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.title.get_text(strip=True) if soup.title else "No Title"
        text = "\n".join(p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 40)
        
        if not text or len(text) < 100:
            print(f"⚠️ Scraped content too short: {url}")
            return {"error": "Content too short"}
        
        return {
            "title": title,
            "text": text,
            "method": "bs4"
        }

    except Exception as e:
        print(f"❌ bs4 scraping failed for {url}:", str(e))
        return {"error": f"Scraping failed: {e}"}
