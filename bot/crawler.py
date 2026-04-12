"""Crawl article tu URL - extract title, text, thumbnail, video."""

from typing import Optional

import requests
from bs4 import BeautifulSoup


def crawl_article(url: str) -> Optional[dict]:
    """Crawl 1 URL, tra ve dict voi title, text, thumbnail, video_url.

    Returns None neu crawl that bai.
    """
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; ContentBot/1.0)"
        })
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"[crawler] Request failed: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    title = _extract_title(soup)
    if not title:
        print(f"[crawler] No title found for {url}")
        return None

    text = _extract_text(soup)
    if not text or len(text) < 100:
        print(f"[crawler] Content too short for {url}")
        return None

    thumbnail = _extract_thumbnail(soup)
    video_url = _extract_video(soup)

    return {
        "source_url": url,
        "title": title,
        "text": text,
        "thumbnail": thumbnail,
        "video_url": video_url,
    }


def _extract_title(soup: BeautifulSoup) -> str:
    """Lay title tu og:title, h1, hoac <title>."""
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return og["content"].strip()

    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    title = soup.find("title")
    if title:
        return title.get_text(strip=True)

    return ""


def _extract_text(soup: BeautifulSoup) -> str:
    """Extract main content text."""
    # Tim article tag truoc
    article = soup.find("article")
    if not article:
        article = soup.find("div", class_=lambda c: c and "content" in c.lower()) if soup else None
    if not article:
        article = soup.find("div", class_=lambda c: c and "post" in c.lower()) if soup else None
    if not article:
        article = soup.body if soup.body else soup

    # Remove script, style, nav, footer
    for tag in article.find_all(["script", "style", "nav", "footer", "aside"]):
        tag.decompose()

    paragraphs = article.find_all("p")
    text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
    return text


def _extract_thumbnail(soup: BeautifulSoup) -> str:
    """Lay thumbnail tu og:image."""
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        return og["content"].strip()
    return ""


def _extract_video(soup: BeautifulSoup) -> str:
    """Tim video URL neu co."""
    # Check og:video
    og = soup.find("meta", property="og:video")
    if og and og.get("content"):
        return og["content"].strip()

    # Check video tag
    video = soup.find("video")
    if video:
        src = video.get("src") or ""
        source = video.find("source")
        if source:
            src = source.get("src", "")
        if src:
            return src.strip()

    return ""
