#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run one due queued publish job")
    p.add_argument("--queue-json", required=True)
    p.add_argument("--rewritten-json", required=True)
    p.add_argument("--facebook-config", required=True)
    p.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN", ""))
    p.add_argument("--sheets-config")
    p.add_argument("--shortlink-base", default="")
    p.add_argument("--out-json", required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    base = Path(__file__).resolve().parents[1]
    py = str(base / ".venv" / "bin" / "python")
    queue_path = Path(args.queue_json)
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    target = None
    for row in queue:
        if row.get("status") == "queued" and row.get("scheduled_time") <= now:
            target = row
            break

    if not target:
        result = {"mode": "no_due_job"}
        Path(args.out_json).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False))
        return

    rewritten_rows = json.loads(Path(args.rewritten_json).read_text(encoding="utf-8"))
    picked = [r for r in rewritten_rows if r.get("job_id") == target.get("job_id")]
    temp_json = base / "runtime" / "queue-picked-job.json"
    temp_json.write_text(json.dumps(picked, indent=2, ensure_ascii=False), encoding="utf-8")

    cmd = [
        py,
        str(base / "scripts" / "run_honghotduong_full_flow.py"),
        "--rewritten-json",
        str(temp_json),
        "--facebook-config",
        args.facebook_config,
        "--github-token",
        args.github_token,
        "--limit",
        "1",
        "--out-json",
        args.out_json,
    ]
    if args.shortlink_base:
        cmd.extend(["--shortlink-base", args.shortlink_base])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        target["status"] = "done"
        queue_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
        if args.sheets_config:
            subprocess.run([
                py,
                str(base / "scripts" / "report_publish_to_sheet.py"),
                "--sheets-config",
                args.sheets_config,
                "--result-json",
                args.out_json,
            ], capture_output=True, text=True)
    else:
        error_text = (proc.stderr or proc.stdout or "publish_queue_failed").strip()
        retryable_tokens = [
            "Error validating access token",
            '"code":190',
            "OAuthException",
            "session is invalid because the user logged out",
        ]
        is_retryable = any(token in error_text for token in retryable_tokens)
        target["status"] = "queued" if is_retryable else "error"
        target["last_error"] = error_text[:500]
        queue_path.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
    print(proc.stdout if proc.stdout else proc.stderr)


if __name__ == "__main__":
    main()
