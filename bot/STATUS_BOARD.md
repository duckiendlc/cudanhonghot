# Bot Status Board

Cap nhat trang thai bot production de ca 2 may cung nam duoc tien do.

## NOW

### In progress
- Chuan hoa repo `cudanhonghot/bot` thanh diem lam viec chung cho ca may WEB va may BOT
- Lap ke hoach migrate logic production tu workspace `projects/content-automation/` vao `bot/`

### Ready next
- Port cum scheduler production vao `bot/`
- Port config rewrite agent vao `bot/`
- Port source registry + multi-source crawl router vao `bot/`
- Chot file entrypoint production cho bot repo

## DONE

- Da xac nhan repo `projects/cudanhonghot` push/pull duoc tren GitHub
- Da them `bot/MIGRATION_PLAN.md`
- Da them `bot/COLLAB_WORKFLOW.md`
- Da cap nhat `bot/README.md` cho shared workflow
- Da ghi nhan trang thai bot vao `NOTES.md`
- Da verify o workspace local:
  - morning chain khong con crash
  - full chain scan -> crawl -> rewrite -> select -> queue build OK
  - publish live that thanh cong: web + Facebook post + Facebook comment

## BLOCKED / RISKS

- Logic production that hien van nam chu yeu o `projects/content-automation/`, chua nam trong `bot/`
- Shortlink van con bug path `s/s/...`
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
