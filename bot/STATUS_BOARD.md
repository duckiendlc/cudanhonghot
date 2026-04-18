# Bot Status Board

Cap nhat trang thai bot production de ca 2 may cung nam duoc tien do.

## NOW

### In progress
- Chuan hoa repo `cudanhonghot/bot` thanh diem lam viec chung cho ca may WEB va may BOT
- Lap ke hoach migrate logic production tu workspace `projects/content-automation/` vao `bot/`

### Ready next
- Port cac dependency con thieu cho `run_morning_chain.py` vao `bot/scripts/`
- Noi scheduler moi vao pipeline bot repo hien tai
- Port source-specific crawlers/rewrite/report helpers con thieu
- Test chay production truc tiep tu repo `bot/`

## DONE

- Da xac nhan repo `projects/cudanhonghot` push/pull duoc tren GitHub
- Da them `bot/MIGRATION_PLAN.md`
- Da them `bot/COLLAB_WORKFLOW.md`
- Da them `bot/STATUS_BOARD.md` va `bot/HANDOFF.md`
- Da cap nhat `bot/README.md` cho shared workflow
- Da ghi nhan trang thai bot vao `NOTES.md`
- Da port cum rewrite config dau tien vao repo bot:
  - `bot/config/content-agent.json`
  - `bot/scripts/rewrite_via_openai.py`
  - `bot/docs/PRODUCTION_ENTRYPOINTS.md`
- Da port them cum scheduler / multi-source / healthcheck / shortlink dau tien vao repo bot:
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
- Da verify o workspace local:
  - morning chain khong con crash
  - full chain scan -> crawl -> rewrite -> select -> queue build OK
  - publish live that thanh cong: web + Facebook post + Facebook comment

## BLOCKED / RISKS

- Nhieu dependency scripts cua scheduler production van chua port het vao `bot/scripts/`
- Scheduler bot repo chua duoc run end-to-end tu chinh repo nay
- Facebook token van co rui ro het han / logout / permission drift
- Co nguy co lech giua workspace local va repo goc neu cham migration

## OWNER SPLIT

### Bot machine
- Port code production vao `bot/`
- Van hanh scheduler / queue / publish
- Theo doi Google Sheet / Facebook / cron

### Web machine
- Ho tro root web neu can sua shortlink / build / preview behavior
- Review output published content
- Dong bo thay doi root repo khi can
