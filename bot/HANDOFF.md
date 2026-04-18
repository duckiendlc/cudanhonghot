# Handoff Log

## 2026-04-18 - BOT -> SHARED REPO

### Da lam
- Xac nhan scheduler production o workspace local co chay that qua cron.
- Tim ra va sua 2 loi chinh trong morning chain local:
  1. crash khi thieu `sheet-check.json`
  2. goi nham system `python3` thay vi project venv, gay loi thieu `gspread`
- Rerun lai full morning chain local va xac nhan toan bo step xanh.
- Chay publish live that thanh cong:
  - web publish OK
  - Facebook post OK
  - Facebook comment OK
- Push len repo goc cac tai lieu de bat dau chuan hoa repo shared.

### Da port them vao repo bot
- `bot/config/content-agent.json`
- `bot/scripts/rewrite_via_openai.py`
- `bot/docs/PRODUCTION_ENTRYPOINTS.md`
- `bot/scripts/run_morning_chain.py`
- `bot/scripts/run_publish_queue_once.py`
- `bot/scripts/run_healthcheck.py`
- `bot/scripts/source_registry.py`
- `bot/scripts/scan_multi_source_targets.py`
- `bot/scripts/source_scan_generic_rss_to_sheet.py`
- `bot/scripts/crawl_jobs_by_source_router.py`
- `bot/scripts/crawl_generic_article_jobs.py`
- `bot/scripts/create_internal_shortlink.py`
- `bot/docs/SCHEDULE_AND_RUNTIME.md`

### Chua xong
- Chua port het dependency scripts scheduler production vao `bot/`.
- Chua noi runner rewrite moi vao pipeline bot repo hien tai.
- Chua test end-to-end full scheduler truc tiep tu repo bot.

### Uu tien tiep theo
1. Port cac dependency con thieu cho scheduler (`load_*`, `seed_*`, `merge_*`, `select_*`, `report_*`, source-specific handlers).
2. Noi rewrite runner moi vao pipeline bot repo.
3. Test end-to-end full scheduler truc tiep tu repo `bot/`.
4. Sau khi on dinh, dua cron/wrapper production bam thang repo `bot/`.

### Ghi chu cho may khac
- Neu muon nam tien do nhanh, doc theo thu tu:
  1. `SYSTEM_GUIDE.md`
  2. `bot/MIGRATION_PLAN.md`
  3. `bot/STATUS_BOARD.md`
  4. file nay
- Trong giai doan chuyen tiep, production that van dang chay o workspace local, nhung repo nay da la noi ghi nhan tien do va ke hoach shared.
