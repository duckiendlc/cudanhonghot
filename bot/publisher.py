"""Publish bai viet len web qua GitHub API.

Su dung bot_client.py (HongHotClient) o root repo.
"""

import os
import sys
import time
from typing import Optional

import requests

# Import HongHotClient tu root repo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from bot_client import HongHotClient


def get_client() -> HongHotClient:
    """Tao HongHotClient tu env vars."""
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO", "duckiendlc/cudanhonghot")
    site_url = os.getenv("SITE_URL", "https://cudanhonghot.online")

    if not token:
        raise ValueError("GITHUB_TOKEN not set in .env")

    return HongHotClient(repo=repo, token=token, site_url=site_url)


def publish_to_web(article: dict) -> Optional[dict]:
    """Publish 1 bai len web. Tra ve result dict hoac None."""
    try:
        client = get_client()
        result = client.create_post(
            title=article["title"],
            content_html=article["content_html"],
            thumbnail=article.get("thumbnail", ""),
            video_url=article.get("video_url", ""),
            description=article.get("description", ""),
            categories=article.get("categories", []),
            tags=article.get("tags", []),
            source_url=article.get("source_url", ""),
        )
        return result
    except Exception as e:
        print(f"[publisher] Failed: {e}", file=sys.stderr)
        return None


def wait_for_deploy(post_url: str, timeout: int = 120, interval: int = 10) -> bool:
    """Poll post_url cho den khi tra ve 200. Timeout sau N giay."""
    print(f"[publisher] Waiting for deploy: {post_url}")
    start = time.time()

    while time.time() - start < timeout:
        try:
            r = requests.head(post_url, timeout=5, allow_redirects=True)
            if r.status_code == 200:
                print(f"[publisher] Deploy confirmed ({int(time.time() - start)}s)")
                return True
        except requests.RequestException:
            pass

        time.sleep(interval)

    print(f"[publisher] Deploy timeout after {timeout}s")
    return False
