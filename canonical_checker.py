import requests
from bs4 import BeautifulSoup

def check_canonical(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        canonical_tag = soup.find("link", rel="canonical")
        canonical_url = canonical_tag["href"] if canonical_tag else None
        return {
            "url": url,
            "canonical": canonical_url,
            "status": canonical_url == url
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e)
        }
