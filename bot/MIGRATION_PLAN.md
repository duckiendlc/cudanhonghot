# Bot Migration Plan - shared production workflow

Mục tiêu: đưa phần content automation production từ workspace local vào repo `cudanhonghot` để nhiều máy cùng pull/push làm việc chung.

## Hiện trạng

Hiện nay có 2 nơi chứa logic bot:

1. `projects/content-automation/`
   - là nơi đang chạy production thật trên máy bot
   - có sheet-driven scheduler, scan/crawl/rewrite/select/queue/publish
   - có cron wrappers, healthcheck, OpenAI rewrite config, shortlink helpers
   - NHƯỢC ĐIỂM: không có remote GitHub riêng, khó cộng tác đa máy

2. `projects/cudanhonghot/bot/`
   - là repo gốc có `origin`
   - push/pull được giữa nhiều máy
   - nhưng hiện code bot ở đây còn đơn giản hơn bản production đang chạy thật

## Quyết định

Repo chuẩn để cộng tác đa máy là:
- `projects/cudanhonghot`
- và phần bot chuẩn sống trong `bot/`

`projects/content-automation/` chỉ nên là vùng thử nghiệm / staging tạm thời cho đến khi migration hoàn tất.

## Mục tiêu migration theo đợt

### Đợt 1 - Đồng bộ tài liệu và contract
- [x] Chốt repo `cudanhonghot/bot` là nơi làm việc chung
- [x] Ghi lại migration plan trong repo gốc
- [ ] Chuẩn hóa README bot cho workflow sheet-driven production
- [ ] Ghi rõ file nào thuộc production, file nào chỉ là experimental

### Đợt 2 - Chuyển cấu hình production tối thiểu
- [ ] Đưa config rewrite agent vào `bot/config/content-agent.json`
- [ ] Đưa prompt/template liên quan vào repo bot
- [ ] Đưa schema Google Sheet/source/job vào `bot/docs/`
- [ ] Chuẩn hóa `.env.example` theo đúng production variables

### Đợt 3 - Chuyển orchestration scheduler
- [ ] Port `run_morning_chain.py` vào `bot/` hoặc `bot/scripts/`
- [ ] Port `run_publish_queue_once.py`
- [ ] Port `run_healthcheck_cron.sh` logic sang bot repo
- [ ] Đảm bảo mọi script dùng cùng interpreter/venv, không gọi lẫn system `python3`

### Đợt 4 - Chuyển source engine đa nguồn
- [ ] Port source registry
- [ ] Port generic RSS scanner
- [ ] Port generic article crawler
- [ ] Port router crawl theo source profile
- [ ] Tách rõ source-specific handlers và generic handlers

### Đợt 5 - Chuyển publish/report hoàn chỉnh
- [ ] Port publish web worker
- [ ] Port FB post/comment runner
- [ ] Port report back to Google Sheet
- [ ] Port shortlink creation + live check

## Nguyên tắc migration

1. Không sửa web root ngoài `bot/` khi chưa cần thiết.
2. Không commit secret, token, `.env`.
3. Chuyển theo cụm production ổn định, không copy toàn bộ thử nghiệm bừa sang repo gốc.
4. Mỗi đợt migrate xong phải chạy test thật được ở bot repo.
5. Khi đã có phiên bản ổn định trong `bot/`, máy khác chỉ cần:
   - `git pull`
   - setup `.env`
   - chạy đúng entrypoint trong `bot/`

## Trạng thái hiện tại cần nhớ

- Morning scheduler ở workspace local đã được sửa để:
  - không crash nếu thiếu `sheet-check.json`
  - dùng đúng project venv thay vì system `python3`
- Đã verify lại full chain chạy xanh và có sinh queue
- Đã verify publish live thật thành công:
  - web publish OK
  - Facebook post OK
  - Facebook comment OK
- Vẫn còn bug phụ ở shortlink path (`s/s/...`) cần sửa ở đợt tiếp theo

## Cách làm việc chung từ bây giờ

Trước mắt:
- mọi thay đổi production cần được phản ánh về repo `projects/cudanhonghot`
- dùng repo này làm message bus + source of truth cho phần bot shared

Trong giai đoạn chuyển tiếp:
- `projects/content-automation/` = nơi sửa/thử nhanh
- `projects/cudanhonghot/bot/` = nơi chốt và push để máy khác cùng làm
