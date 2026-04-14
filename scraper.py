"""
scraper.py — Crawls the target website and saves all page text to a local JSON file.
Run this once before indexing into ChromaDB.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time

from config import BASE_URL, SEED_URLS, SCRAPED_OUTPUT


def is_same_domain(url: str) -> bool:
    base_netloc = urlparse(BASE_URL).netloc
    netloc = urlparse(url).netloc
    return netloc in (base_netloc, f"www.{base_netloc}", "")


def clean_text(soup: BeautifulSoup) -> str:
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())


def scrape_url(url: str) -> tuple:
    """Returns (text, discovered_links) or (None, []) on failure."""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"  Skipped (status {resp.status_code})")
            return None, []
        soup = BeautifulSoup(resp.text, "html.parser")
        text = clean_text(soup)
        links = []
        for a in soup.find_all("a", href=True):
            full_url = urljoin(url, a["href"])
            full_url = full_url.split("#")[0].split("?")[0]
            if is_same_domain(full_url) and full_url.startswith("http"):
                links.append(full_url)
        return text, links
    except Exception as e:
        print(f"  Error: {e}")
        return None, []


def scrape_site() -> list:
    visited = set()
    queue = list(SEED_URLS)
    pages = []

    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        print(f"Scraping: {url}")
        text, links = scrape_url(url)

        if text:
            pages.append({"url": url, "content": text})
            print(f"  OK — {len(text)} chars")

        for link in links:
            if link not in visited and link not in queue:
                queue.append(link)

        time.sleep(0.5)

    return pages


if __name__ == "__main__":
    print(f"Starting scrape of {BASE_URL} ...\n")
    pages = scrape_site()

    with open(SCRAPED_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Scraped {len(pages)} pages -> saved to {SCRAPED_OUTPUT}")
    for p in pages:
        print(f"  {p['url']}")
