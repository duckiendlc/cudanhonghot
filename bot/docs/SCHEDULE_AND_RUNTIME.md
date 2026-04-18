# Schedule and Runtime Overview

Tai lieu nay mo ta bot production schedule sau khi migration vao repo `bot/`.

## Scheduler production

### Morning chain
- Thoi gian muc tieu: `05:00` moi ngay
- Entrypoint: `bot/scripts/run_morning_chain.py`
- Nhiem vu:
  1. scan source tu Google Sheet
  2. load candidates/jobs
  3. seed jobs
  4. route jobs theo source profile
  5. crawl
  6. rewrite local + OpenAI rewrite
  7. select
  8. check duplicate/status tren sheet
  9. build queue publish trong ngay

### Publish queue
- Tan suat muc tieu: moi `15 phut`
- Entrypoint: `bot/scripts/run_publish_queue_once.py`
- Nhiem vu:
  - lay job due trong `queue.json`
  - publish web
  - dang Facebook
  - comment link
  - report ket qua ve sheet

### Healthcheck
- Chay nhieu moc trong ngay
- Entrypoint: `bot/scripts/run_healthcheck.py`
- Nhiem vu:
  - kiem tra artifact runtime trong ngay
  - canh bao queue/rewrite/crawl missing
  - canh bao step fail
  - canh bao token/session/GitHub blocker

## Multi-source engine

### Registry
- `bot/scripts/source_registry.py`
- Detect source profile theo host/platform/source_type

### Scanner
- `bot/scripts/scan_multi_source_targets.py`
- `bot/scripts/source_scan_generic_rss_to_sheet.py`

### Crawl router
- `bot/scripts/crawl_jobs_by_source_router.py`
- `bot/scripts/crawl_generic_article_jobs.py`
- source-specific crawlers se duoc port them dan

## Shortlink
- Entrypoint: `bot/scripts/create_internal_shortlink.py`
- Da sua logic tao `short_url` thanh:
  - `{site_url}/s/{post_id}/`
- tranh bug path kieu `s/s/...`

## Runtime layout huong den

```text
bot/
  runtime/
    scheduled-morning-YYYY-MM-DD/
      summary.json
      queue.json
      crawl.json
      rewrite.json
      rewrite-openai.json
    publish-run-YYYY-MM-DD.json
    healthcheck-YYYY-MM-DD.json
```

## Luu y hien tai
- Day la migration dang dien ra.
- Chua phai tat ca dependency scripts da duoc port xong vao `bot/scripts/`.
- Nhung repo da bat dau chua ro entrypoints production va runtime contract de 2 may co cung cach nhin he thong.
