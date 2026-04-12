"""Pipeline orchestrator - dieu phoi toan bo flow.

Flow: scan -> crawl -> rewrite -> filter -> publish -> fb_post
"""

import os
import sys

from scanner import scan_sources
from crawler import crawl_article
from rewriter import rewrite_content
from publisher import publish_to_web, wait_for_deploy
from fb_poster import post_to_facebook, comment_shortlink


def run_pipeline() -> dict:
    """Chay full pipeline. Tra ve stats dict."""
    max_posts = int(os.getenv("MAX_POSTS_PER_RUN", "5"))

    stats = {"scanned": 0, "published": 0, "fb_posted": 0, "skipped": 0}

    # Step 1-2: Scan sources
    print("[pipeline] Scanning sources...")
    candidates = scan_sources()
    stats["scanned"] = len(candidates)
    print(f"[pipeline] Found {len(candidates)} candidates")

    for i, candidate in enumerate(candidates[:max_posts]):
        print(f"\n[pipeline] Processing {i+1}/{min(len(candidates), max_posts)}: {candidate['url']}")

        try:
            # Step 3-4: Crawl + extract
            article = crawl_article(candidate["url"])
            if not article:
                print(f"[pipeline] Skip: crawl failed")
                stats["skipped"] += 1
                continue

            # Step 5: Rewrite
            rewritten = rewrite_content(article)
            if not rewritten:
                print(f"[pipeline] Skip: rewrite failed")
                stats["skipped"] += 1
                continue

            # Step 6: Filter usable
            if not rewritten.get("content_html") or not rewritten.get("title"):
                print(f"[pipeline] Skip: missing title or content")
                stats["skipped"] += 1
                continue

            # Step 7: Publish to web
            result = publish_to_web(rewritten)
            if not result:
                print(f"[pipeline] Skip: publish failed")
                stats["skipped"] += 1
                continue

            stats["published"] += 1
            print(f"[pipeline] Published: {result['post_url']}")

            # Step 8: Wait for deploy
            if not wait_for_deploy(result["post_url"]):
                print(f"[pipeline] Warning: deploy not confirmed, posting FB anyway")

            # Step 9-10: Post to Facebook + comment shortlink
            fb_ok = post_to_facebook(rewritten, result)
            if fb_ok:
                stats["fb_posted"] += 1
                print(f"[pipeline] FB posted + commented")
            else:
                print(f"[pipeline] FB post failed")

        except Exception as e:
            print(f"[pipeline] Error: {e}", file=sys.stderr)
            stats["skipped"] += 1
            continue

    return stats
