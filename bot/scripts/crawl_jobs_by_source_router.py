#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from source_registry import detect_source_profile

DEFAULT_SOURCE_RUNNER = "crawl_generic_article_jobs.py"
SOURCE_RUNNERS = {
    "honghotduong_like": "crawl_honghotduong_jobs.py",
    "generic_website": "crawl_generic_article_jobs.py",
    "generic_source": "crawl_generic_article_jobs.py",
    "facebook_stub": "crawl_generic_article_jobs.py",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Route pending jobs to crawler scripts by source_id")
    p.add_argument("--routed-jobs-json", required=True)
    p.add_argument("--sheets-config", required=True)
    p.add_argument("--out-json", required=True)
    return p.parse_args()


def load_source_rows(sheets_config_path: str) -> dict[str, dict]:
    import gspread
    from google.oauth2.service_account import Credentials

    cfg = json.loads(Path(sheets_config_path).read_text(encoding="utf-8"))
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(cfg["serviceAccountPath"], scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(cfg["spreadsheetId"])
    ws = sh.worksheet(cfg["tabs"]["sources"])
    rows = ws.get_all_records()
    return {str(row.get("source_id", "")).strip(): row for row in rows if str(row.get("source_id", "")).strip()}


def main() -> None:
    args = parse_args()
    base = Path(__file__).resolve().parents[1]
    routed = json.loads(Path(args.routed_jobs_json).read_text(encoding="utf-8"))
    source_rows = load_source_rows(args.sheets_config)
    results = []

    for source_id, jobs in routed.items():
        valid_jobs = [j for j in jobs if str(j.get("source_post_url", "")).strip()]
        skipped_jobs = [j for j in jobs if not str(j.get("source_post_url", "")).strip()]
        source_row = source_rows.get(source_id, {})
        profile = detect_source_profile(source_row) if source_row else None
        script_name = SOURCE_RUNNERS.get(profile.parser_key if profile else "", DEFAULT_SOURCE_RUNNER if valid_jobs else None)
        if not script_name:
            results.append({
                "source_id": source_id,
                "job_count": len(jobs),
                "valid_job_count": len(valid_jobs),
                "skipped_job_count": len(skipped_jobs),
                "mode": "skipped",
                "reason": "no_crawler_registered",
            })
            continue
        out_json = base / "runtime" / f"crawl-{source_id}.json"
        jobs_json = base / "runtime" / f"jobs-{source_id}.json"
        jobs_json.write_text(json.dumps(valid_jobs, indent=2, ensure_ascii=False), encoding="utf-8")
        cmd = [
            str(base / ".venv" / "bin" / "python"),
            str(base / "scripts" / script_name),
            "--sheets-config",
            args.sheets_config,
            "--jobs-json",
            str(jobs_json),
            "--out-json",
            str(out_json),
            "--limit",
            str(len(valid_jobs)),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        results.append({
            "source_id": source_id,
            "job_count": len(jobs),
            "valid_job_count": len(valid_jobs),
            "skipped_job_count": len(skipped_jobs),
            "parser_key": profile.parser_key if profile else "unknown",
            "crawler_key": profile.crawler_key if profile else "unknown",
            "skipped_jobs": [
                {
                    "job_id": str(j.get("job_id", "")).strip(),
                    "reason": "missing_source_post_url",
                }
                for j in skipped_jobs
            ],
            "mode": "ran",
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "out_json": str(out_json),
        })

    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"sources": len(results), "out_json": args.out_json}, ensure_ascii=False))


if __name__ == "__main__":
    main()
