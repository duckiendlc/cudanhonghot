"""Rewrite noi dung bai viet.

TODO: Tich hop AI rewrite (OpenAI/Claude API) de viet lai noi dung.
Hien tai chi clean up va format lai.
"""

import re
from typing import Optional


def rewrite_content(article: dict) -> Optional[dict]:
    """Rewrite article content. Tra ve dict san sang publish.

    Input: dict tu crawler (title, text, thumbnail, video_url, source_url)
    Output: dict voi title, content_html, description, thumbnail, video_url, source_url
    """
    title = article.get("title", "").strip()
    text = article.get("text", "").strip()

    if not title or not text:
        return None

    # Clean up text
    text = _clean_text(text)

    # Convert text to HTML paragraphs
    content_html = _text_to_html(text)

    # Generate description (2 cau dau)
    description = _make_description(text)

    return {
        "title": title,
        "content_html": content_html,
        "description": description,
        "thumbnail": article.get("thumbnail", ""),
        "video_url": article.get("video_url", ""),
        "source_url": article.get("source_url", ""),
        "categories": [],
        "tags": [],
    }


def _clean_text(text: str) -> str:
    """Lam sach text: bo khoang trang thua, dong trong."""
    # Bo nhieu dong trong lien tiep
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Bo khoang trang dau/cuoi moi dong
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def _text_to_html(text: str) -> str:
    """Convert plain text thanh HTML paragraphs."""
    paragraphs = text.split("\n\n")
    html_parts = []
    for p in paragraphs:
        p = p.strip()
        if p:
            # Escape HTML
            p = p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_parts.append(f"<p>{p}</p>")
    return "\n".join(html_parts)


def _make_description(text: str, max_len: int = 160) -> str:
    """Tao description tu 1-2 cau dau."""
    sentences = re.split(r"[.!?]\s+", text)
    desc = ""
    for s in sentences[:2]:
        if len(desc) + len(s) > max_len:
            break
        desc += s.strip() + ". "
    return desc.strip() or text[:max_len].strip()
