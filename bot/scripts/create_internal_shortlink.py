#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from bot_client import HongHotClient  # noqa: E402

HTML_TEMPLATE = """<!doctype html>
<html lang=\"vi\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <meta http-equiv=\"refresh\" content=\"0; url={target_url}\">
  <link rel=\"canonical\" href=\"{target_url}\">
  <title>{page_title}</title>
  <meta name=\"description\" content=\"{page_description}\">
  <meta property=\"og:locale\" content=\"vi_VN\">
  <meta property=\"og:type\" content=\"article\">
  <meta property=\"og:title\" content=\"{page_title}\">
  <meta property=\"og:description\" content=\"{page_description}\">
  <meta property=\"og:url\" content=\"{short_url}\">
  <meta property=\"og:site_name\" content=\"Cư Dân Hóng Hớt\">
  <meta name=\"twitter:card\" content=\"summary\">
  <meta name=\"twitter:title\" content=\"{page_title}\">
  <meta name=\"twitter:description\" content=\"{page_description}\">
  <script>location.replace({target_url_json});</script>
</head>
<body>
  <p>Đang chuyển hướng tới bài viết. Nếu không tự chuyển, bấm <a href=\"{target_url}\">vào đây</a>.</p>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create an internal shortlink redirect page in the web repo")
    p.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN", ""))
    p.add_argument("--repo", default="duckiendlc/cudanhonghot")
    p.add_argument("--site-url", default="https://cudanhonghot.online")
    p.add_argument("--post-id", required=True)
    p.add_argument("--target-url", required=True)
    p.add_argument("--title", default="")
    p.add_argument("--description", default="")
    p.add_argument("--out-json", required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not args.github_token:
        raise SystemExit("Missing GitHub token")

    client = HongHotClient(repo=args.repo, token=args.github_token, site_url=args.site_url)
    short_path = f"s/{args.post_id}/index.html"
    short_url = f"{args.site_url.rstrip('/')}/s/{args.post_id}/"
    page_title = (args.title or "Xem bài đầy đủ tại Cư Dân Hóng Hớt").strip()
    page_description = (args.description or "Bấm để mở bài viết đầy đủ trên Cư Dân Hóng Hớt.").strip()
    html = HTML_TEMPLATE.format(
        target_url=args.target_url,
        target_url_json=json.dumps(args.target_url),
        page_title=page_title,
        page_description=page_description,
        short_url=short_url,
    )
    client._put_file(short_path, html, f"shortlink: {args.post_id}")

    result = {
        "post_id": args.post_id,
        "target_url": args.target_url,
        "short_path": short_path,
        "short_url": short_url,
        "title": page_title,
        "description": page_description,
    }
    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
