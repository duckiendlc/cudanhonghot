#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scan a generic RSS feed and write candidates/jobs into Google Sheet")
    p.add_argument("--source-config", required=True)
    p.add_argument("--sheets-config", required=True)
    p.add_argument("--selection-limit", type=int)
    return p.parse_args()


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "GT-AGENT/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def parse_feed(feed_xml: str) -> list[dict]:
    root = ET.fromstring(feed_xml)
    channel = root.find("channel")
    if channel is None:
        return []
    items = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date_raw = (item.findtext("pubDate") or "").strip()
        desc = (item.findtext("description") or "").strip()
        category = (item.findtext("category") or "").strip()
        pub_dt = parsedate_to_datetime(pub_date_raw) if pub_date_raw else None
        if pub_dt is not None and pub_dt.tzinfo is None:
            pub_dt = pub_dt.replace(tzinfo=timezone.utc)
        items.append(
            {
                "title": title,
                "link": link,
                "pub_date_raw": pub_date_raw,
                "pub_date_iso": pub_dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z") if pub_dt else "",
                "description": strip_html(desc),
                "category": category,
            }
        )
    return items


def get_client(service_account_path: str):
    creds = Credentials.from_service_account_file(service_account_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_existing_urls(ws) -> set[str]:
    records = ws.get_all_records()
    return {
        str(row.get("source_post_url", "")).strip()
        for row in records
        if str(row.get("source_post_url", "")).strip()
    }


def append_rows_dict(ws, rows: list[dict]) -> None:
    if not rows:
        return
    headers = ws.row_values(1)
    values = [[row.get(h, "") for h in headers] for row in rows]
    ws.append_rows(values, value_input_option="USER_ENTERED")


def main() -> None:
    args = parse_args()
    source_cfg = load_json(args.source_config)
    sheets_cfg = load_json(args.sheets_config)
    selection_limit = args.selection_limit or int(source_cfg.get("selectionLimit", 3))

    gc = get_client(sheets_cfg["serviceAccountPath"])
    sh = gc.open_by_key(sheets_cfg["spreadsheetId"])
    candidates_ws = sh.worksheet(sheets_cfg["tabs"]["candidates"])
    jobs_ws = sh.worksheet(sheets_cfg["tabs"]["jobs"])

    known_urls = get_existing_urls(candidates_ws)
    feed_text = fetch_text(source_cfg["feedUrl"])
    items = parse_feed(feed_text)
    new_items = [item for item in items if item["link"] and item["link"] not in known_urls]
    new_items.sort(key=lambda x: x["pub_date_iso"], reverse=True)
    selected = new_items[:selection_limit]
    scanned_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")
    batch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    source_tag = str(source_cfg.get("sourceId", "SRC")).upper()

    candidates_rows = []
    jobs_rows = []
    for idx, item in enumerate(new_items, start=1):
        candidate_id = f"CAND_{source_tag}_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{idx:03d}"
        is_selected = "yes" if item in selected else "no"
        candidates_rows.append(
            {
                "candidate_id": candidate_id,
                "source_id": source_cfg["sourceId"],
                "detected_at": scanned_at,
                "source_post_id": item["link"],
                "source_post_url": item["link"],
                "source_title": item["title"],
                "source_publish_time": item["pub_date_iso"],
                "like_count": "",
                "comment_count": "",
                "share_count": "",
                "view_count": "",
                "engagement_score": "",
                "is_selected": is_selected,
                "selection_batch_date": batch_date,
                "status": "selected" if is_selected == "yes" else "new",
                "note": item["category"],
                "last_error": "",
            }
        )
        if is_selected == "yes":
            jobs_rows.append(
                {
                    "job_id": f"JOB_{source_tag}_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{len(jobs_rows)+1:03d}",
                    "candidate_id": candidate_id,
                    "source_id": source_cfg["sourceId"],
                    "source_post_url": item["link"],
                    "source_title": item["title"],
                    "status": "queued",
                    "crawl_status": "pending",
                    "rewrite_status": "pending",
                    "facebook_post_status": "pending",
                    "web_post_status": "pending",
                    "comment_status": "pending",
                    "facebook_caption_short": "",
                    "thumbnail_url": "",
                    "facebook_post_id": "",
                    "facebook_post_url": "",
                    "published_url": "",
                    "last_run_at": "",
                    "note": item["description"][:180],
                    "last_error": "",
                }
            )

    append_rows_dict(candidates_ws, candidates_rows)
    append_rows_dict(jobs_ws, jobs_rows)

    print(json.dumps({
        "source": source_cfg.get("sourceName", source_cfg["sourceId"]),
        "feed_url": source_cfg["feedUrl"],
        "feed_items": len(items),
        "new_items": len(new_items),
        "selected_items": len(selected),
        "candidates_appended": len(candidates_rows),
        "jobs_appended": len(jobs_rows),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
