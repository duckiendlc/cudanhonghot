#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path


def load_dotenv_if_present() -> None:
    env_path = Path(__file__).resolve().parents[1] / '.env'
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Rewrite content using OpenAI Chat Completions API")
    p.add_argument("--payload-json", required=True)
    p.add_argument("--out-json", required=True)
    p.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / 'config' / 'content-agent.json'))
    p.add_argument("--model")
    return p.parse_args()


def normalize_item(item: dict, caption_ending: str, weak_content_max_html_length: int) -> dict:
    quality_notes = item.get("quality_notes", [])
    if isinstance(quality_notes, str):
        quality_notes = [quality_notes] if quality_notes.strip() else []
    elif not isinstance(quality_notes, list):
        quality_notes = []
    quality_notes = [str(x).strip() for x in quality_notes if str(x).strip()]

    fb = str(item.get("facebook_caption_short", "")).strip()
    if fb and not fb.endswith(caption_ending):
        fb = fb.rstrip(" .") + f"\n\n{caption_ending}"

    web_body_html = str(item.get("web_body_html", "")).strip()
    if "weak_content" in quality_notes and len(web_body_html) > weak_content_max_html_length:
        web_body_html = ""

    return {
        "job_id": str(item.get("job_id", "")).strip(),
        "web_title": str(item.get("web_title", "")).strip(),
        "web_body_html": web_body_html,
        "web_summary": str(item.get("web_summary", "")).strip(),
        "facebook_caption_short": fb,
        "quality_notes": quality_notes,
    }


def main() -> None:
    args = parse_args()
    load_dotenv_if_present()
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY in environment")

    cfg = load_json(Path(args.config))
    openai_cfg = cfg.get("openai", {})
    rewrite_cfg = cfg.get("rewrite", {})

    model = args.model or os.environ.get("OPENAI_REWRITE_MODEL") or openai_cfg.get("model", "gpt-4o-mini")
    temperature = float(openai_cfg.get("temperature", 0.7))
    response_format = openai_cfg.get("responseFormat", "json_object")
    system_prompt = rewrite_cfg.get("systemPrompt", "")
    user_prompt_template = rewrite_cfg.get("userPromptTemplate", "INPUT JSON:\n{payload_json}\n\nTrả về object có key 'items' là array kết quả.")
    caption_ending = rewrite_cfg.get("facebookCaptionEnding", "Chi tiết ở phần bình luận.")
    weak_content_max_html_length = int(rewrite_cfg.get("weakContentMaxHtmlLength", 400))

    payload_text = Path(args.payload_json).read_text(encoding="utf-8")
    user_prompt = user_prompt_template.replace("{payload_json}", payload_text)

    body = {
        "model": model,
        "response_format": {"type": response_format},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        raw = json.loads(resp.read().decode("utf-8"))

    content = raw["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    items = [normalize_item(x, caption_ending, weak_content_max_html_length) for x in parsed.get("items", [])]

    out = Path(args.out_json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"items": len(items), "out_json": args.out_json, "model": model, "config": args.config}, ensure_ascii=False))


if __name__ == "__main__":
    main()
