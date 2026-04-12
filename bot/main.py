#!/usr/bin/env python3
"""Content automation pipeline - entry point.

Chay: python main.py
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from pipeline import run_pipeline


def main():
    print("[bot] Starting content automation pipeline...")
    try:
        stats = run_pipeline()
        print(f"[bot] Done. Published: {stats['published']}, "
              f"FB posted: {stats['fb_posted']}, "
              f"Skipped: {stats['skipped']}")
    except Exception as e:
        print(f"[bot] Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
