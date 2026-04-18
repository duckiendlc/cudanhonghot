#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from source_registry import detect_source_profile

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scan active content sources from Google Sheet")
    p.add_argument("--sheets-config", required=True)
    p.add_argument("--out-json", required=True)
    return p.parse_args()


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_client(service_account_path: str):
    creds = Credentials.from_service_account_file(service_account_path, scopes=SCOPES)
    return gspread.authorize(creds)


def truthy(value) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def build_source_config(base: Path, row: dict, profile) -> Path:
    out_path = base / "runtime" / f"source-config-{row['source_id']}.json"
    cfg = {
        "sourceId": row["source_id"],
        "sourceName": row.get("source_name") or row["source_id"],
        "feedUrl": profile.feed_url,
        "siteUrl": profile.site_url or row.get("target_link") or "",
        "selectionLimit": int(row.get("selection_limit") or 3),
        "parserKey": profile.parser_key,
        "scannerKey": profile.scanner_key,
        "crawlerKey": profile.crawler_key,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def main() -> None:
    args = parse_args()
    base = Path(__file__).resolve().parents[1]
    sheets_cfg = load_json(args.sheets_config)
    py = str(base / ".venv" / "bin" / "python")

    gc = get_client(sheets_cfg["serviceAccountPath"])
    sh = gc.open_by_key(sheets_cfg["spreadsheetId"])
    ws = sh.worksheet(sheets_cfg["tabs"]["sources"])
    rows = ws.get_all_records()

    results = []
    for row in rows:
        if not truthy(row.get("active")):
            continue

        source_id = str(row.get("source_id", "")).strip()
        target_link = str(row.get("target_link", "")).strip()
        source_type = str(row.get("source_type", "")).strip().lower()
        platform = str(row.get("platform", "")).strip().lower()
        profile = detect_source_profile(row)

        if not profile or not profile.feed_url:
            results.append({
                "source_id": source_id,
                "platform": platform,
                "source_type": source_type,
                "target_link": target_link,
                "returncode": 0,
                "stdout": "",
                "stderr": "unsupported_source_for_current_scanner",
            })
            continue

        source_cfg = build_source_config(base, row, profile)
        scanner_script = "source_scan_generic_rss_to_sheet.py"
        if profile.parser_key == "honghotduong_like":
            scanner_script = "source_scan_honghotduong_to_sheet.py"
        cmd = [
            py,
            str(base / "scripts" / scanner_script),
            "--source-config",
            str(source_cfg),
            "--sheets-config",
            args.sheets_config,
            "--selection-limit",
            str(int(row.get("selection_limit") or 3)),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        results.append({
            "source_id": source_id,
            "platform": platform,
            "source_type": source_type,
            "target_link": target_link,
            "parser_key": profile.parser_key,
            "scanner_key": profile.scanner_key,
            "crawler_key": profile.crawler_key,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        })

    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"sources": len(results), "out_json": args.out_json}, ensure_ascii=False))


if __name__ == "__main__":
    main()
