#!/usr/bin/env python3
"""Static site builder for Cư Dân Hóng Hớt.

Reads posts/*.json -> renders HTML via Jinja2 -> outputs to dist/.
Run locally: python build.py
CI: runs in .github/workflows/build.yml on push.
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import SITE, AFF

ROOT = Path(__file__).parent
POSTS_DIR = ROOT / "posts"
STATIC_DIR = ROOT / "static"
TEMPLATES_DIR = ROOT / "templates"
DIST = ROOT / "dist"


def load_posts():
    """Load tất cả file JSON trong posts/ và validate field cơ bản."""
    posts = []
    for f in sorted(POSTS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"[SKIP] {f.name}: JSON lỗi - {e}", file=sys.stderr)
            continue

        if not data.get("title") or not data.get("content_html"):
            print(f"[SKIP] {f.name}: thiếu title hoặc content_html", file=sys.stderr)
            continue

        # slug = filename không có .json, trừ khi JSON tự set
        data.setdefault("slug", f.stem)
        data.setdefault("date", datetime.now().strftime("%Y-%m-%d"))
        data.setdefault("description", "")
        data.setdefault("thumbnail", "")
        data.setdefault("video_url", "")
        data.setdefault("categories", [])
        data.setdefault("tags", [])
        data["url"] = f"/post/{data['slug']}/"
        data["canonical"] = SITE["url"] + data["url"]
        posts.append(data)

    # Mới nhất trước
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    return posts


def clean_dist():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)


def copy_static():
    """Copy static/ -> dist/ (styles, js, logo, CNAME, favicon)."""
    if not STATIC_DIR.exists():
        return
    for item in STATIC_DIR.iterdir():
        dest = DIST / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)


def render(env, template_name, output_path, **context):
    tpl = env.get_template(template_name)
    html = tpl.render(site=SITE, aff=AFF, **context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def main():
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    posts = load_posts()
    clean_dist()
    copy_static()

    # Home
    render(env, "index.html", DIST / "index.html", posts=posts)

    # 404
    render(env, "404.html", DIST / "404.html")

    # Từng bài
    for p in posts:
        out = DIST / "post" / p["slug"] / "index.html"
        render(env, "post.html", out, post=p)

    # Simple sitemap.xml cho SEO + FB crawler
    urls = [SITE["url"] + "/"] + [p["canonical"] for p in posts]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        sitemap += f"  <url><loc>{u}</loc></url>\n"
    sitemap += "</urlset>\n"
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    print(f"[build] {len(posts)} posts -> {DIST}")


if __name__ == "__main__":
    main()
