# Production Entrypoints - bot repo

Tai lieu nay chot cac cum entrypoint production se song trong repo `bot/` sau migration.

## Muc tieu

May BOT phai co the chay production truc tiep tu repo nay, khong phu thuoc vao workspace local rieng.

## Cum production uu tien cao

### 1. Rewrite agent config + runner
Da dua vao repo:
- `bot/config/content-agent.json`
- `bot/scripts/rewrite_via_openai.py`

Muc dich:
- prompt/model/rule cho rewrite duoc version control trong repo goc
- may khac pull ve se dung cung prompt rewrite, khong bi lech giua cac may

### 2. Morning scheduler chain
Muc tieu file sau khi port:
- `bot/scripts/run_morning_chain.py`
- `bot/scripts/run_publish_queue_once.py`
- `bot/scripts/run_healthcheck.py` hoac script wrapper tuong duong

Yeu cau:
- dung cung mot venv interpreter
- khong goi lan system `python3`
- neu thieu artifact trung gian thi khong crash ca chain
- luon ghi ra `summary.json` + `queue.json` de de theo doi

### 3. Multi-source engine
Muc tieu file sau khi port:
- source registry
- sheet-source scanner
- crawl router
- generic crawler
- source-specific crawler/rewrite handlers

## Cau truc huong den

```text
bot/
  config/
    content-agent.json
    ...
  docs/
    PRODUCTION_ENTRYPOINTS.md
    ...
  scripts/
    rewrite_via_openai.py
    run_morning_chain.py
    run_publish_queue_once.py
    ...
  runtime/
    .gitkeep
```

## Trang thai hien tai

- Rewrite config/runner da co mat trong repo bot
- Scheduler va multi-source engine chua port xong, van dang chay o workspace local
- Sau moi dot port, can cap nhat `STATUS_BOARD.md` va `HANDOFF.md`
