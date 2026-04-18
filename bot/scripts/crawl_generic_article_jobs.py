#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from html import unescape
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

ARTICLE_RE = re.compile(r'<article.*?</article>', re.DOTALL | re.IGNORECASE)
TITLE_RE = re.compile(r'<title>(.*?)</title>', re.DOTALL | re.IGNORECASE)
OG_IMAGE_RE = re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', re.IGNORECASE)
PARA_RE = re.compile(r'<p[^>]*>(.*?)</p>', re.DOTALL | re.IGNORECASE)
IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
VIDEO_RE = re.compile(r'<video[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
TAG_RE = re.compile(r'<[^>]+>')


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Crawl generic article jobs from JSON or Google Sheet")
    p.add_argument("--sheets-config", required=True)
    p.add_argument("--out-json", required=True)
    p.add_argument("--limit", type=int, default=3)
    p.add_argument("--jobs-json")
    return p.parse_args()


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_client(service_account_path: str):
    creds = Credentials.from_service_account_file(service_account_path, scopes=SCOPES)
    return gspread.authorize(creds)


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "GT-AGENT/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def clean_text(html: str) -> str:
    text = TAG_RE.sub(" ", html)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_article(html: str) -> dict:
    title_match = TITLE_RE.search(html)
    og_image_match = OG_IMAGE_RE.search(html)
    article_match = ARTICLE_RE.search(html)
    article_html = article_match.group(0) if article_match else html
    paragraphs = [clean_text(p) for p in PARA_RE.findall(article_html)]
    paragraphs = [p for p in paragraphs if p]
    images = IMG_RE.findall(article_html)
    videos = VIDEO_RE.findall(article_html)
    return {
        "page_title": clean_text(title_match.group(1)) if title_match else "",
        "og_image": og_image_match.group(1) if og_image_match else "",
        "article_text": "\n\n".join(paragraphs),
        "article_paragraphs": paragraphs,
        "images": images,
        "videos": videos,
        "has_video": bool(videos),
    }


def append_logs(ws, rows: list[list[str]]) -> None:
    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")


def main() -> None:
    args = parse_args()
    cfg = load_json(args.sheets_config)
    gc = get_client(cfg["serviceAccountPath"])
    sh = gc.open_by_key(cfg["spreadsheetId"])
    jobs_ws = sh.worksheet(cfg["tabs"]["jobs"])
    logs_ws = sh.worksheet(cfg["tabs"]["logs"])

    if args.jobs_json:
        records = json.loads(Path(args.jobs_json).read_text(encoding="utf-8"))
    else:
        records = jobs_ws.get_all_records()
    queued = [r for r in records if str(r.get("status", "")).strip().lower() == "queued"]
    queued = queued[: args.limit]

    crawled = []
    log_rows = []
    for row in queued:
        job_id = str(row.get("job_id", "")).strip()
        url = str(row.get("source_post_url", "")).strip()
        title = str(row.get("source_title", "")).strip()
        try:
            html = fetch_html(url)
            article = extract_article(html)
            thumbnail = article["og_image"] or (article["images"][0] if article["images"] else "")
            crawled.append(
                {
                    "job_id": job_id,
                    "source_post_url": url,
                    "source_title": title,
                    "page_title": article["page_title"],
                    "thumbnail_url": thumbnail,
                    "article_text": article["article_text"],
                    "article_paragraphs": article["article_paragraphs"],
                    "images": article["images"],
                    "videos": article["videos"],
                    "has_video": article["has_video"],
                }
            )
            log_rows.append(["", "crawler", "info", "job", job_id, "Crawled generic article successfully", url])
        except Exception as e:
            log_rows.append(["", "crawler", "error", "job", job_id, "Failed to crawl generic article", f"{url} :: {e}"])

    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(crawled, indent=2, ensure_ascii=False), encoding="utf-8")
    append_logs(logs_ws, log_rows)

    print(json.dumps({"queued_jobs": len(queued), "crawled_jobs": len(crawled), "out_json": args.out_json}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
