import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

def fetch_text_from_url(url: str, max_chars=3000) -> str:
    """
    Fetch and extract text content from a URL.
    Returns extracted text or error message.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; HarmWatch/1.0; +https://example.com)"
        }
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return f"[Error fetching URL: status {resp.status_code}]"
        
        soup = BeautifulSoup(resp.text, "html.parser")
        parts = []
        
        # Extract title
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        if title:
            parts.append(title)
        
        # Extract Open Graph description
        og = soup.find("meta", property="og:description")
        if og and og.get("content"):
            parts.append(og.get("content").strip())
        
        # Extract meta description
        m = soup.find("meta", attrs={"name": "description"})
        if m and m.get("content"):
            parts.append(m.get("content").strip())
        
        # Extract text from common content tags
        texts = []
        for tag in soup.find_all(["p", "li", "span", "strong", "h1", "h2", "h3", "h4", "h5", "h6"]):
            t = tag.get_text(separator=" ", strip=True)
            if t and len(t) > 20:
                texts.append(t)
        
        if texts:
            parts.append(" ".join(texts[:8]))
        
        combined = "\n\n".join(parts)
        if not combined.strip():
            combined = soup.get_text(separator=" ", strip=True)[:max_chars]
        
        return combined[:max_chars]
    except Exception as e:
        return f"[Error fetching URL: {e}]"

def extract_domains_from_url(url: str) -> list:
    """
    Extract domain names from a URL.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return [domain]
    except Exception:
        return []

def is_social_media_url(url: str) -> bool:
    """
    Check if URL is from a social media platform.
    """
    social_domains = {
        'twitter.com', 'x.com', 'facebook.com', 'instagram.com', 
        'youtube.com', 'tiktok.com', 'linkedin.com', 'reddit.com'
    }
    domains = extract_domains_from_url(url)
    return any(domain in social_domains for domain in domains)

def analyze_url(url: str) -> dict:
    """
    Comprehensive URL analysis.
    Returns dict with extracted text, domains, and metadata.
    """
    text = fetch_text_from_url(url)
    domains = extract_domains_from_url(url)
    
    return {
        "url": url,
        "extracted_text": text,
        "domains": domains,
        "is_social_media": is_social_media_url(url),
        "success": not text.startswith("[Error")
    }
