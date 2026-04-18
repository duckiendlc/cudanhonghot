# Collaboration Workflow - 2 machine shared repo

Muc tieu: ca may WEB va may BOT cung lam viec tren cung repo, nhin vao repo la biet:
- ai dang lam gi
- phan nao da xong
- phan nao dang block
- buoc tiep theo la gi

## Nguyen tac lam viec chung

1. Luon `git pull --rebase origin main` truoc khi sua.
2. Khong sua lan nhau o cac vung da chia ro trach nhiem.
3. Moi thay doi dang lam phai duoc ghi vao `bot/STATUS_BOARD.md`.
4. Khi ban giao giua 2 may, cap nhat `bot/HANDOFF.md`.
5. Khi co quyet dinh ky thuat moi, cap nhat `bot/MIGRATION_PLAN.md` hoac docs lien quan.

## Phan chia trach nhiem de tranh dam chan

### May WEB
Thuong xu ly:
- web root neu duoc yeu cau ro rang
- giao dien, templates, build behavior
- shortlink / page behavior o root repo
- review output bai da publish

### May BOT
Thuong xu ly:
- `bot/` folder
- scheduler
- scan / crawl / rewrite / select / queue / publish
- Google Sheet integration
- Facebook publish / comment
- healthcheck / logs / cron wrappers

## File dung chung de theo doi tien do

### 1. `bot/STATUS_BOARD.md`
Dung de theo doi theo module:
- todo
- doing
- blocked
- done

### 2. `bot/HANDOFF.md`
Dung de ghi ban giao giua 2 may:
- vua sua gi
- test ra sao
- dang block o dau
- may kia can tiep tuc viec gi

### 3. `NOTES.md`
Dung cho ghi chu muc cao cap cap repo, ngan gon, de ca 2 ben doc nhanh.

## Commit convention khuyen dung

- `bot: ...` cho logic automation
- `docs: ...` cho tai lieu / tracker / handoff
- `fix: ...` cho sua loi production
- `web: ...` cho thay doi ben web

## Nhip lam viec khuyen dung

### Truoc khi bat dau
1. `git pull --rebase origin main`
2. Doc:
   - `SYSTEM_GUIDE.md`
   - `bot/STATUS_BOARD.md`
   - `bot/HANDOFF.md`
3. Chon 1 cum viec nho, ro pham vi

### Trong luc lam
- Neu dang xu ly 1 muc quan trong, danh dau `IN PROGRESS` trong `bot/STATUS_BOARD.md`
- Neu co blocker that, ghi ngay vao `bot/HANDOFF.md`

### Ket thuc mot dot
1. Cap nhat `bot/STATUS_BOARD.md`
2. Cap nhat `bot/HANDOFF.md`
3. Commit
4. Push

## Muc tieu repo chuan

Repo nay duoc coi la chuan khi:
- logic production cua bot song trong `bot/`
- may BOT chay truc tiep tu repo nay
- may WEB co the pull va review / sua phan lien quan ma khong can nhin workspace rieng
- tien do duoc theo doi ngay trong repo, khong phu thuoc chat log
