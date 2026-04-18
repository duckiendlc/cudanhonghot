#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class SourceProfile:
    parser_key: str
    scanner_key: str
    crawler_key: str
    feed_url: str | None = None
    site_url: str | None = None


def normalize_host(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower().strip()
    except Exception:
        host = ""
    return host.removeprefix("www.")


def detect_source_profile(row: dict) -> SourceProfile | None:
    target_link = str(row.get("target_link", "")).strip()
    platform = str(row.get("platform", "")).strip().lower()
    source_type = str(row.get("source_type", "")).strip().lower()
    host = normalize_host(target_link)

    if host in {"honghotduong.com", "honghotduongpho.club"}:
        return SourceProfile(
            parser_key="honghotduong_like",
            scanner_key="rss_generic",
            crawler_key="article_html_generic",
            feed_url="https://honghotduong.com/feed/" if host == "honghotduong.com" else "https://www.honghotduongpho.club/feed/",
            site_url=target_link,
        )

    if platform == "website" and target_link:
        return SourceProfile(
            parser_key="generic_website",
            scanner_key="rss_generic",
            crawler_key="article_html_generic",
            feed_url=f"{target_link.rstrip('/')}/feed/",
            site_url=target_link,
        )

    if platform == "facebook":
        return SourceProfile(
            parser_key="facebook_stub",
            scanner_key="facebook_stub",
            crawler_key="article_html_generic",
            feed_url=None,
            site_url=target_link,
        )

    if source_type in {"source", "category", "page"} and target_link:
        return SourceProfile(
            parser_key="generic_source",
            scanner_key="rss_generic",
            crawler_key="article_html_generic",
            feed_url=f"{target_link.rstrip('/')}/feed/",
            site_url=target_link,
        )

    return None
