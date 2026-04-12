# System Guide - cudanhonghot.online

Tai lieu cho AI/developer ben may bot hieu kien truc va thao tac dung.

## Repo nay la gi

Monorepo gom 2 phan:
- **Web** (root) — static site, deploy len GitHub Pages tai `cudanhonghot.online`
- **Bot** (`bot/`) — Python pipeline tu dong crawl tin → rewrite → publish web → post Facebook

## Kien truc tong the

```
Google Sheet (source URLs)
    ↓
Bot Python (bot/) — chay tren may Linux ARM64
    ↓ crawl + rewrite
    ↓ git push JSON vao posts/
GitHub Repo (duckiendlc/cudanhonghot)
    ↓ trigger
GitHub Actions → build static HTML → deploy GitHub Pages
    ↓
cudanhonghot.online (live)
    ↓
Bot → post bai ngan len Facebook Page → comment shortlink
    ↓
Facebook Users → click shortlink → doc bai tren web → thay affiliate banner
```

## KHONG DUOC LAM

1. **KHONG sua truc tiep file trong `dist/`** — folder nay do `build.py` generate, moi lan build se xoa sach va tao lai
2. **KHONG commit file `.env`, `credentials.json`** — chua secret tokens, da gitignore
3. **KHONG doi ten/xoa cac file goc cua web** — `build.py`, `config.py`, `bot_client.py`, `templates/`, `static/` la core cua web. Doi se break build
4. **KHONG push truc tiep vao `dist/` hay `posts/` bang tay** — dung `bot_client.py` (HongHotClient) de tao bai, no xu ly slug, uniquify, commit message dung format
5. **KHONG doi format file JSON trong `posts/`** — schema co dinh, thieu `title` hoac `content_html` se bi skip khi build
6. **KHONG xoa `.github/workflows/build.yml`** — day la pipeline deploy. Xoa = web khong tu dong update
7. **KHONG sua `CNAME` trong `static/`** — domain config cho GitHub Pages
8. **KHONG commit PAT, FB token, Google credentials** vao bat ky file nao ngoai `.env`

## Cau truc thu muc

```
cudanhonghot/
├── .github/workflows/build.yml  ← CI/CD: build + deploy GitHub Pages
├── bot/                         ← Bot content automation
│   ├── main.py                  ← Entry point: python main.py
│   ├── pipeline.py              ← Dieu phoi 10 buoc
│   ├── scanner.py               ← B1-2: scan Google Sheet
│   ├── crawler.py               ← B3-4: crawl URL, extract text/video
│   ├── rewriter.py              ← B5: rewrite noi dung
│   ├── publisher.py             ← B6-8: publish web qua GitHub API
│   ├── fb_poster.py             ← B9-10: post FB + comment shortlink
│   ├── .env.example             ← Template config (copy thanh .env)
│   └── requirements.txt         ← Python dependencies
├── bot_client.py                ← SDK dung chung: HongHotClient
├── build.py                     ← Static site generator (Jinja2)
├── config.py                    ← Site config + affiliate config
├── templates/                   ← Jinja2 HTML templates
│   ├── index.html               ← Home (2 bai moi nhat)
│   ├── post.html                ← Bai viet chi tiet
│   └── 404.html                 ← Trang loi
├── static/                      ← CSS, logo, favicon, CNAME
├── posts/                       ← Bai viet JSON (bot tao, build doc)
├── s/                           ← Shortlink redirect HTML
├── dist/                        ← OUTPUT (gitignored, do build.py tao)
├── API_CONTRACT.md              ← API doc cho bot
└── SYSTEM_GUIDE.md              ← TAI LIEU NAY
```

## Flow tao bai viet

### Bot tu dong (bot/main.py)

```
1. scanner.py    → doc Google Sheet, lay URL chua xu ly
2. crawler.py    → crawl URL, extract title/text/thumbnail/video
3. rewriter.py   → rewrite noi dung (hien tai: clean + format)
4. publisher.py  → goi HongHotClient.create_post()
                   → tao posts/{id}.json
                   → git push vao repo
                   → GitHub Actions tu build + deploy
5. publisher.py  → poll URL cho den khi 200 (deploy xong)
6. fb_poster.py  → POST bai ngan len Facebook Page (Graph API)
7. fb_poster.py  → comment shortlink duoi bai
```

### Tao bai thu cong (dung SDK)

```python
from bot_client import HongHotClient

client = HongHotClient(
    repo="duckiendlc/cudanhonghot",
    token="ghp_xxx",
    site_url="https://cudanhonghot.online",
)

result = client.create_post(
    title="Tieu de bai",
    content_html="<p>Noi dung...</p>",
    thumbnail="https://example.com/thumb.jpg",
    description="Mo ta ngan cho FB preview",
)
# result["post_url"] = https://cudanhonghot.online/post/20260412-tieu-de-bai/
```

## Schema JSON bai viet

File: `posts/{YYYYMMDD}-{slug}.json`

```json
{
  "title": "BAT BUOC — tieu de bai",
  "content_html": "BAT BUOC — noi dung HTML",
  "date": "YYYY-MM-DD",
  "description": "mo ta ngan, hien tren FB preview",
  "thumbnail": "URL anh, og:image",
  "video_url": "URL MP4 neu co",
  "categories": ["Drama"],
  "tags": ["nong"],
  "source_url": "URL bai goc"
}
```

**Luu y:** `title` va `content_html` la bat buoc. Thieu 1 trong 2 → bai bi skip khi build.

## Build flow (web)

```
posts/*.json → build.py (Python + Jinja2) → dist/ → GitHub Pages
```

- `build.py` doc tat ca `posts/*.json`
- Render HTML tu `templates/` voi data tu JSON + `config.py`
- Output ra `dist/` (index.html, post/{slug}/index.html, sitemap.xml)
- GitHub Actions upload `dist/` len Pages

## Shortlink

- Format: `cudanhonghot.online/s/{post_id}/`
- File: `s/{post_id}/index.html` — meta refresh + JS redirect den `/post/{post_id}/`
- Bot nen dung shortlink khi comment FB de URL ngan gon

## Facebook integration

- Dung Facebook Graph API v19.0
- Can: `FB_PAGE_ID` + `FB_PAGE_TOKEN` (Page Access Token)
- Post bai ngan (title + description) len page feed
- Comment shortlink duoi post
- FB tu lay OG tags tu web de hien preview

## Config

### config.py (web)
- `SITE` — ten, URL, description, language
- `AFF` — affiliate URL, banner image

### bot/.env (bot secrets)
- `GITHUB_TOKEN` — PAT de push bai
- `GITHUB_REPO` — `duckiendlc/cudanhonghot`
- `SITE_URL` — `https://cudanhonghot.online`
- `FB_PAGE_ID`, `FB_PAGE_TOKEN` — Facebook
- `GOOGLE_SHEET_ID`, `GOOGLE_CREDENTIALS_FILE` — Google Sheets

## Troubleshooting

| Van de | Nguyen nhan | Fix |
|--------|-------------|-----|
| Bai khong hien tren web | Build loi hoac JSON thieu field | Check GitHub Actions log |
| 404 sau khi tao bai | Build chua xong (~30-60s) | Doi hoac check Actions |
| FB preview sai/cu | FB cache | Scrape lai tai fb.com/tools/debug |
| Bot 401 | Token het han | Tao PAT moi |
| Bot 403 | Token thieu quyen | Them scope contents:write |
| Shortlink khong redirect | Thieu file s/{id}/index.html | Tao bang bot hoac thu cong |

## Luu y cho AI/developer

- Khi sua `templates/` hoac `build.py` → push len, GitHub Actions tu build lai toan bo site
- Khi sua `bot/` → chi anh huong bot, web khong bi anh huong
- Khi sua `config.py` → anh huong ca web (site name, affiliate) nen can trigger rebuild
- `bot_client.py` o root duoc dung boi ca `bot/publisher.py` (import tu parent dir) — KHONG move/rename
- Moi thay doi push len `main` branch se tu dong trigger build + deploy
