#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run full morning content chain: scan -> crawl/rewrite/select -> sheet check -> queue build")
    p.add_argument("--sheets-config", required=True)
    p.add_argument("--facebook-config", required=True)
    p.add_argument("--out-dir", required=True)
    return p.parse_args()


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "command": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def main() -> None:
    args = parse_args()
    base = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    py = str(base / ".venv" / "bin" / "python")

    artifacts = {
        "scan": out_dir / "scan.json",
        "candidates_sheet": out_dir / "candidates-sheet.json",
        "top_candidates": out_dir / "top-candidates.json",
        "jobs_sheet": out_dir / "jobs-sheet.json",
        "seeded_jobs": out_dir / "seeded-jobs.json",
        "filtered_seeded_jobs": out_dir / "filtered-seeded-jobs.json",
        "jobs_effective": out_dir / "jobs-effective.json",
        "routed_jobs": out_dir / "routed-jobs.json",
        "crawl_router": out_dir / "crawl-router.json",
        "crawl": out_dir / "crawl.json",
        "rewrite": out_dir / "rewrite.json",
        "rewrite_agent_payload": out_dir / "rewrite-agent-payload.json",
        "rewrite_openai": out_dir / "rewrite-openai.json",
        "selected": out_dir / "selected.json",
        "sheet_check": out_dir / "sheet-check.json",
        "queue": out_dir / "queue.json",
    }

    steps = []

    steps.append({
        "name": "scan",
        **run([
            py,
            str(base / "scripts" / "scan_multi_source_targets.py"),
            "--sheets-config",
            args.sheets_config,
            "--out-json",
            str(artifacts["scan"]),
        ]),
    })

    steps.append({
        "name": "load_candidates_sheet",
        **run([
            py,
            str(base / "scripts" / "load_candidates_from_sheet.py"),
            "--sheets-config",
            args.sheets_config,
            "--out-json",
            str(artifacts["candidates_sheet"]),
        ]),
    })

    steps.append({
        "name": "select_top_candidates",
        **run([
            py,
            str(base / "scripts" / "select_top_candidates_per_source.py"),
            "--candidates-json",
            str(artifacts["candidates_sheet"]),
            "--out-json",
            str(artifacts["top_candidates"]),
            "--per-source-limit",
            "10",
        ]),
    })

    steps.append({
        "name": "load_jobs_sheet",
        **run([
            py,
            str(base / "scripts" / "load_jobs_from_sheet.py"),
            "--sheets-config",
            args.sheets_config,
            "--out-json",
            str(artifacts["jobs_sheet"]),
        ]),
    })

    steps.append({
        "name": "seed_jobs",
        **run([
            py,
            str(base / "scripts" / "seed_jobs_from_top_candidates.py"),
            "--top-candidates-json",
            str(artifacts["top_candidates"]),
            "--existing-jobs-json",
            str(artifacts["jobs_sheet"]),
            "--out-json",
            str(artifacts["seeded_jobs"]),
            "--limit",
            "3",
        ]),
    })

    steps.append({
        "name": "filter_seeded_jobs",
        **run([
            py,
            str(base / "scripts" / "filter_seeded_jobs.py"),
            "--seeded-json",
            str(artifacts["seeded_jobs"]),
            "--out-json",
            str(artifacts["filtered_seeded_jobs"]),
        ]),
    })

    steps.append({
        "name": "append_seeded_jobs_to_sheet",
        **run([
            py,
            str(base / "scripts" / "append_seeded_jobs_to_sheet.py"),
            "--sheets-config",
            args.sheets_config,
            "--seeded-json",
            str(artifacts["filtered_seeded_jobs"]),
        ]),
    })

    try:
        seeded_jobs = json.loads(artifacts["filtered_seeded_jobs"].read_text(encoding="utf-8"))
    except Exception:
        seeded_jobs = []
    if seeded_jobs:
        artifacts["jobs_effective"].write_text(json.dumps(seeded_jobs, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        artifacts["jobs_effective"].write_text(artifacts["jobs_sheet"].read_text(encoding="utf-8"), encoding="utf-8")

    steps.append({
        "name": "route_jobs",
        **run([
            py,
            str(base / "scripts" / "route_jobs_from_sheet.py"),
            "--jobs-json",
            str(artifacts["jobs_effective"]),
            "--out-json",
            str(artifacts["routed_jobs"]),
        ]),
    })

    steps.append({
        "name": "crawl_router",
        **run([
            py,
            str(base / "scripts" / "crawl_jobs_by_source_router.py"),
            "--routed-jobs-json",
            str(artifacts["routed_jobs"]),
            "--sheets-config",
            args.sheets_config,
            "--out-json",
            str(artifacts["crawl_router"]),
        ]),
    })

    steps.append({
        "name": "merge_crawl_outputs",
        **run([
            py,
            str(base / "scripts" / "merge_crawl_router_outputs.py"),
            "--crawl-router-json",
            str(artifacts["crawl_router"]),
            "--out-json",
            str(artifacts["crawl"]),
        ]),
    })

    steps.append({
        "name": "rewrite",
        **run([
            py,
            str(base / "scripts" / "rewrite_honghotduong_jobs.py"),
            "--input-json",
            str(artifacts["crawl"]),
            "--out-json",
            str(artifacts["rewrite"]),
        ]),
    })

    steps.append({
        "name": "rewrite_agent_payload",
        **run([
            py,
            str(base / "scripts" / "prepare_rewrite_agent_payload.py"),
            "--rewritten-json",
            str(artifacts["rewrite"]),
            "--out-json",
            str(artifacts["rewrite_agent_payload"]),
        ]),
    })

    rewrite_source = artifacts["rewrite"]
    steps.append({
        "name": "rewrite_openai",
        **run([
            py,
            str(base / "scripts" / "rewrite_via_openai.py"),
            "--payload-json",
            str(artifacts["rewrite_agent_payload"]),
            "--out-json",
            str(artifacts["rewrite_openai"]),
        ]),
    })
    if steps[-1]["returncode"] == 0 and artifacts["rewrite_openai"].exists():
        try:
            openai_rows = json.loads(artifacts["rewrite_openai"].read_text(encoding="utf-8"))
        except Exception:
            openai_rows = []
        try:
            local_rows = json.loads(artifacts["rewrite"].read_text(encoding="utf-8"))
        except Exception:
            local_rows = []
        local_map = {str(row.get("job_id", "")).strip(): row for row in local_rows}
        merged_openai = []
        for row in openai_rows:
            job_id = str(row.get("job_id", "")).strip()
            local_row = local_map.get(job_id, {})
            merged = dict(local_row)
            merged.update(row)
            merged_openai.append(merged)
        artifacts["rewrite_openai"].write_text(json.dumps(merged_openai, indent=2, ensure_ascii=False), encoding="utf-8")
        usable_openai = [
            row for row in merged_openai
            if "weak_content" not in [str(x).strip().lower() for x in (row.get("quality_notes") or [])]
            and bool(row.get("thumbnail_url"))
            and len(str(row.get("facebook_caption_short", "")).strip()) > 0
            and len(str(row.get("web_body_html", "") or row.get("web_body", "")).strip()) >= 160
        ]
        if usable_openai:
            rewrite_source = artifacts["rewrite_openai"]

    steps.append({
        "name": "select",
        **run([
            py,
            str(base / "scripts" / "select_publishable_jobs.py"),
            "--rewritten-json",
            str(rewrite_source),
            "--out-json",
            str(artifacts["selected"]),
            "--limit",
            "3",
        ]),
    })

    steps.append({
        "name": "sheet_check",
        **run([
            py,
            str(base / "scripts" / "check_jobs_sheet_before_post.py"),
            "--sheets-config",
            args.sheets_config,
            "--selected-json",
            str(artifacts["selected"]),
            "--out-json",
            str(artifacts["sheet_check"]),
        ]),
    })

    selected_after_check = []
    if artifacts["sheet_check"].exists():
        try:
            selected_after_check = json.loads(artifacts["sheet_check"].read_text(encoding="utf-8")).get("selected", [])
        except Exception:
            selected_after_check = []
            steps.append({
                "name": "sheet_check_recover",
                "command": ["internal"],
                "returncode": 1,
                "stdout": "",
                "stderr": "sheet_check.json exists but could not be parsed",
            })
    else:
        steps.append({
            "name": "sheet_check_recover",
            "command": ["internal"],
            "returncode": 1,
            "stdout": "",
            "stderr": "sheet_check.json was not created, falling back to empty selection",
        })

    temp_selected = out_dir / "selected-after-sheet.json"
    temp_selected.write_text(json.dumps(selected_after_check, indent=2, ensure_ascii=False), encoding="utf-8")

    steps.append({
        "name": "queue_build",
        **run([
            py,
            str(base / "scripts" / "build_spread_schedule.py"),
            "--selected-json",
            str(temp_selected),
            "--out-json",
            str(artifacts["queue"]),
            "--count",
            "3",
            "--start",
            "05:00",
            "--end",
            "23:59",
            "--min-gap-minutes",
            "15",
        ]),
    })

    summary = {
        "artifacts": {k: str(v) for k, v in artifacts.items()},
        "steps": steps,
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"summary": str(summary_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
