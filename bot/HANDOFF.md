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

### Chua xong
- Chua port logic scheduler production tu `projects/content-automation/` vao `bot/`.
- Chua port multi-source engine vao `bot/`.
- Chua sua bug shortlink path `s/s/...`.
- Chua noi runner rewrite moi vao pipeline bot repo hien tai.

### Uu tien tiep theo
1. Port scheduler production (`run_morning_chain`, `run_publish_queue_once`, healthcheck) vao `bot/`.
2. Port multi-source registry/router/scanner/crawler vao `bot/`.
3. Noi rewrite runner moi vao pipeline bot repo.
4. Sau moi cum port, test chay that tu repo `bot/`.

### Ghi chu cho may khac
- Neu muon nam tien do nhanh, doc theo thu tu:
  1. `SYSTEM_GUIDE.md`
  2. `bot/MIGRATION_PLAN.md`
  3. `bot/STATUS_BOARD.md`
  4. file nay
- Trong giai doan chuyen tiep, production that van dang chay o workspace local, nhung repo nay da la noi ghi nhan tien do va ke hoach shared.
