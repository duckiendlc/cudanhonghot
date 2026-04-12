# Bot Content Automation

Tu dong crawl tin tuc, rewrite, publish len web va dang Facebook.

## Setup

```bash
cd bot
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
cp .env.example .env        # dien token vao
```

## Cau hinh

Tao file `.env` tu `.env.example`:

- `GITHUB_TOKEN` — GitHub PAT (scope: contents:write)
- `GITHUB_REPO` — repo name (vd: duckiendlc/cudanhonghot)
- `SITE_URL` — URL web (vd: https://cudanhonghot.online)
- `FB_PAGE_ID` — Facebook Page ID
- `FB_PAGE_TOKEN` — Facebook Page Access Token
- `GOOGLE_SHEET_ID` — Google Sheet chua source URLs

## Chay

```bash
# Chay 1 lan
python main.py

# Hoac setup cron (Linux)
crontab -e
# 0 */2 * * * cd /path/to/bot && .venv/bin/python main.py >> logs/bot.log 2>&1
```

## Pipeline

1. Scan source URLs tu Google Sheet
2. Crawl + extract text/video/thumbnail
3. Rewrite noi dung
4. Filter bai usable
5. Publish len web (git push JSON qua GitHub API)
6. Doi GitHub Pages build xong
7. Post bai ngan len Facebook Page
8. Comment shortlink duoi post
