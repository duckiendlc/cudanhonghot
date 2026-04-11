# Cư Dân Hóng Hớt

Static blog site tự build, tích hợp bot Python tự động đăng bài. Host free trên GitHub Pages.

**Live**: https://cudanhonghot.online

## Kiến trúc

```
posts/*.json  →  build.py (Jinja2)  →  dist/  →  GitHub Pages
     ↑
Python bot (bot_client.py) commit qua GitHub API
```

- **Hosting**: GitHub Pages (free)
- **Builder**: Python + Jinja2 (`build.py`)
- **Data**: JSON files trong `posts/`
- **Auto deploy**: GitHub Actions (`.github/workflows/build.yml`)
- **Bot SDK**: `bot_client.py` (Python + requests)

## Cấu trúc repo

```
├── build.py              # Static site generator
├── config.py             # Site + affiliate config
├── requirements.txt      # jinja2
├── bot_client.py         # Python SDK cho bot
├── API_CONTRACT.md       # Tài liệu cho team automation
├── posts/                # File JSON mỗi bài
│   └── YYYYMMDD-slug.json
├── templates/            # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── post.html
│   └── 404.html
├── static/               # Static assets (copy vào dist/)
│   ├── styles.css
│   ├── app.js            # Logic banner affiliate
│   ├── logo.svg
│   └── CNAME
├── .github/workflows/
│   └── build.yml         # CI: build + deploy Pages
└── dist/                 # Output build (gitignored)
```

## Local development

```bash
pip install -r requirements.txt
python build.py
# Mở dist/index.html hoặc:
python -m http.server 8000 --directory dist
```

## Tạo bài mới (qua bot)

Xem [`API_CONTRACT.md`](./API_CONTRACT.md) — tài liệu chi tiết cho bot Python.

Ngắn gọn:
```python
from bot_client import HongHotClient

client = HongHotClient(
    repo="duckiendlc/cudanhonghot",
    token=os.environ["GITHUB_TOKEN"],
    site_url="https://cudanhonghot.online",
)

result = client.create_post(
    title="...",
    content_html="<p>...</p>",
    thumbnail="https://...",
    video_url="https://...",
    description="...",
)
print(result["post_url"])
```

## Tạo bài thủ công

Thêm file `posts/YYYYMMDD-slug.json` theo schema trong `API_CONTRACT.md`, commit + push → Action tự build & deploy.

## Config affiliate banner

Sửa `config.py`:
```python
AFF = {
    "affiliate_url": "https://link-aff-cua-ban.com",
    "banner_image": "https://url-anh-banner.jpg",
}
```

Commit + push → deploy lại.
