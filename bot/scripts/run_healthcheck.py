#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Healthcheck scheduled bot artifacts")
    p.add_argument("--base-dir", default=str(Path(__file__).resolve().parents[1]))
    p.add_argument("--out-json", required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    base = Path(args.base_dir)
    today = datetime.now().strftime("%Y-%m-%d")
    runtime_dir = base / "runtime" / f"scheduled-morning-{today}"
    queue_path = runtime_dir / "queue.json"
    rewrite_path = runtime_dir / "rewrite.json"
    crawl_path = runtime_dir / "crawl.json"
    summary_path = runtime_dir / "summary.json"

    warnings = []
    errors = []

    queue = load_json(queue_path, []) if queue_path.exists() else []
    rewrite = load_json(rewrite_path, []) if rewrite_path.exists() else []
    crawl = load_json(crawl_path, []) if crawl_path.exists() else []
    summary = load_json(summary_path, {}) if summary_path.exists() else {}
    publish_run = load_json(base / "runtime" / f"publish-run-{today}.json", {})
    steps = summary.get("steps", []) if isinstance(summary, dict) else []

    if not runtime_dir.exists():
        errors.append("scheduled morning runtime dir missing")
    if not crawl_path.exists():
        warnings.append("crawl.json missing")
    if not rewrite_path.exists():
        warnings.append("rewrite.json missing")
    if not queue_path.exists():
        warnings.append("queue.json missing")
    if crawl_path.exists() and not crawl:
        warnings.append("crawl produced 0 items")
    if rewrite_path.exists() and not rewrite:
        warnings.append("rewrite produced 0 items")
    if queue_path.exists() and not queue:
        warnings.append("queue produced 0 publishable jobs")

    for step in steps:
        if step.get("returncode", 0) != 0:
            errors.append(f"step_failed:{step.get('name')} rc={step.get('returncode')}")
        stderr = (step.get("stderr") or "").strip()
        if stderr:
            warnings.append(f"step_stderr:{step.get('name')}::{stderr[:300]}")

    publish_text = json.dumps(publish_run, ensure_ascii=False)
    if publish_run.get("mode") == "no_due_job":
        warnings.append("publish_queue:no_due_job")
    if 'Error validating access token' in publish_text or '"code": 190' in publish_text or '"code":190' in publish_text:
        errors.append("facebook_token_invalid_or_logged_out")
    if 'Missing GitHub token' in publish_text:
        errors.append("github_token_missing_for_publish")

    checks = {
        "timestamp": datetime.now().isoformat(),
        "runtime_dir_exists": runtime_dir.exists(),
        "queue_exists": queue_path.exists(),
        "rewrite_exists": rewrite_path.exists(),
        "crawl_exists": crawl_path.exists(),
        "summary_exists": summary_path.exists(),
        "counts": {
            "crawl_items": len(crawl) if isinstance(crawl, list) else 0,
            "rewrite_items": len(rewrite) if isinstance(rewrite, list) else 0,
            "queue_items": len(queue) if isinstance(queue, list) else 0,
        },
        "warnings": warnings,
        "errors": errors,
    }
    checks["status"] = "fail" if errors else ("warn" if warnings else "ok")

    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(checks, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
