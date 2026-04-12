"""Post bai len Facebook Page va comment shortlink."""

import os
from typing import Optional

import requests

GRAPH_API = "https://graph.facebook.com/v19.0"


def get_fb_config() -> dict:
    """Lay FB config tu env."""
    page_id = os.getenv("FB_PAGE_ID")
    token = os.getenv("FB_PAGE_TOKEN")

    if not page_id or not token:
        raise ValueError("FB_PAGE_ID and FB_PAGE_TOKEN must be set in .env")

    return {"page_id": page_id, "token": token}


def post_to_facebook(article: dict, publish_result: dict) -> bool:
    """Post bai ngan len FB page + comment shortlink.

    Args:
        article: dict voi title, description
        publish_result: dict tu publisher (post_url, post_id)

    Returns True neu thanh cong.
    """
    try:
        config = get_fb_config()
    except ValueError as e:
        print(f"[fb] Config error: {e}")
        return False

    site_url = os.getenv("SITE_URL", "https://cudanhonghot.online")
    post_id = publish_result.get("post_id", "")
    shortlink = f"{site_url}/s/{post_id}/"

    # Step 1: Post bai ngan
    fb_post_id = _create_post(
        config=config,
        message=f"{article['title']}\n\n{article.get('description', '')}",
    )

    if not fb_post_id:
        return False

    # Step 2: Comment shortlink
    ok = _create_comment(
        config=config,
        post_id=fb_post_id,
        message=f"Doc full tai day: {shortlink}",
    )

    return ok


def _create_post(config: dict, message: str) -> Optional[str]:
    """Tao post tren FB page. Tra ve post_id."""
    url = f"{GRAPH_API}/{config['page_id']}/feed"

    try:
        r = requests.post(url, data={
            "message": message,
            "access_token": config["token"],
        }, timeout=15)
        r.raise_for_status()
        data = r.json()
        post_id = data.get("id")
        print(f"[fb] Posted: {post_id}")
        return post_id
    except requests.RequestException as e:
        print(f"[fb] Post failed: {e}")
        return None


def _create_comment(config: dict, post_id: str, message: str) -> bool:
    """Comment len 1 FB post."""
    url = f"{GRAPH_API}/{post_id}/comments"

    try:
        r = requests.post(url, data={
            "message": message,
            "access_token": config["token"],
        }, timeout=15)
        r.raise_for_status()
        print(f"[fb] Commented on {post_id}")
        return True
    except requests.RequestException as e:
        print(f"[fb] Comment failed: {e}")
        return False
