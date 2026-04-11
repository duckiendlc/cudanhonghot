# API Contract - Cư Dân Hóng Hớt

Tài liệu cho bot Python tích hợp đăng bài tự động.

## Kiến trúc

```
Python Bot → GitHub REST API → Repo (posts/*.json) → GitHub Action → GitHub Pages
                                                                    ↓
                                                       https://cudanhonghot.online/post/{id}/
```

- **API endpoint**: GitHub REST API (`https://api.github.com`)
- **Auth**: Bearer token (GitHub Personal Access Token - PAT)
- **Data format**: JSON file trong folder `posts/`
- **Deploy**: tự động qua GitHub Actions (~30-60s sau khi commit)
- **SDK**: `bot_client.py` trong repo (Python wrapper)

---

## 1. Tạo Personal Access Token (PAT)

Làm 1 lần cho bot:

1. Vào https://github.com/settings/tokens?type=beta
2. **Generate new token** → **Fine-grained token**
3. Tên: `cudanhonghot-bot`
4. Expiration: 90 ngày / 1 năm / no expiry tuỳ bạn
5. **Repository access**: Only select repositories → chọn `cudanhonghot`
6. **Permissions** → Repository permissions:
   - **Contents**: Read and write
7. **Generate token** → copy token `github_pat_xxx...`
8. Lưu vào env var của bot: `export GITHUB_TOKEN=github_pat_xxx`

⚠️ Token không hiển thị lại, mất thì phải tạo cái mới.

---

## 2. Sử dụng Python SDK (khuyên dùng)

```python
import os
from bot_client import HongHotClient

client = HongHotClient(
    repo="duckiendlc/cudanhonghot",
    token=os.environ["GITHUB_TOKEN"],
    site_url="https://cudanhonghot.online",
)

# Tạo bài
result = client.create_post(
    title="Drama X vs Y gây sốt MXH",
    content_html="<p>Nội dung bài đã clean...</p><p>...</p>",
    description="Tóm tắt 1-2 câu - sẽ hiện trong FB preview",
    thumbnail="https://cdn.abc.com/thumb.jpg",
    video_url="https://cdn.videy.co/abc.mp4",  # optional
    categories=["Drama"],
    tags=["nong", "hot", "mxh"],
    source_url="https://honghotduong.com/bai-goc",
)

print(result["post_url"])
# → https://cudanhonghot.online/post/20260411-drama-x-vs-y-gay-sot-mxh/

# Xóa bài
client.delete_post("20260411-drama-x-vs-y-gay-sot-mxh")

# List bài
ids = client.list_posts()
```

### Return value của `create_post`
```python
{
    "post_id": "20260411-drama-x-vs-y-gay-sot-mxh",
    "post_url": "https://cudanhonghot.online/post/20260411-drama-x-vs-y-gay-sot-mxh/",
    "build_url": "https://github.com/duckiendlc/cudanhonghot/actions",
    "raw_path": "posts/20260411-drama-x-vs-y-gay-sot-mxh.json",
}
```

### Đợi build xong trước khi comment FB
GitHub Action mất ~30-60s để build + deploy. Bot nên poll URL cho tới khi 200:

```python
import time, requests

def wait_live(url, timeout=180):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.head(url, timeout=5, allow_redirects=True)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(5)
    return False

wait_live(result["post_url"])
# → True khi bài đã live, bot bắt đầu short link + comment FB
```

---

## 3. Gọi trực tiếp GitHub API (không qua SDK)

Nếu không muốn dùng `bot_client.py`, gọi REST API trực tiếp:

### Endpoint
```
PUT https://api.github.com/repos/duckiendlc/cudanhonghot/contents/posts/{post_id}.json
```

### Headers
```
Authorization: Bearer github_pat_xxx
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
```

### Body
```json
{
  "message": "post: Drama X vs Y",
  "branch": "main",
  "content": "<base64 của JSON payload>"
}
```

Content là base64 của file JSON dưới. Xem [GitHub API docs](https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents).

---

## 4. Schema JSON của bài viết

File: `posts/{post_id}.json`. `post_id` tự sinh theo format `YYYYMMDD-{slug}`.

```json
{
  "title": "string, BẮT BUỘC",
  "date": "YYYY-MM-DD, optional (mặc định today)",
  "description": "string, optional - hiện trong FB preview. Không có thì fallback về title",
  "thumbnail": "URL, optional - og:image, FB preview. Không có thì fallback về logo",
  "video_url": "URL MP4, optional - render thẻ <video> trong bài",
  "categories": ["Drama", "Tin tức"],
  "tags": ["nong", "hot"],
  "source_url": "URL nguồn gốc, optional",
  "content_html": "HTML content, BẮT BUỘC - hỗ trợ <p>, <h2>, <img>, <video>, <iframe>, <a>..."
}
```

### Các field bot BẮT BUỘC điền
- `title`
- `content_html`

### Các field QUAN TRỌNG cho FB preview
- `description` - quyết định text dưới link FB
- `thumbnail` - ảnh preview (nên dùng ảnh 1200x630 cho đẹp)

### Các field optional
- `date`, `video_url`, `categories`, `tags`, `source_url`

### Sanitize content_html
Bot nên clean HTML trước khi đăng:
- Bỏ `<script>`, `<style>`, `onclick=`, `javascript:` (tránh XSS)
- Chỉ giữ tag safe: `p, h1-h6, a, img, video, iframe, ul, ol, li, strong, em, blockquote, br, code`
- Library gợi ý: [bleach](https://pypi.org/project/bleach/)

---

## 5. URL bài viết

Format: `https://cudanhonghot.online/post/{post_id}/`

Ví dụ: `https://cudanhonghot.online/post/20260411-drama-x-vs-y/`

URL này là URL bot sẽ:
1. Short bằng bit.ly / cuttly / v.gd
2. Comment lên FB page với link đã short

FB sẽ tự lấy OG tags (title, description, image, video) từ trang này để hiện preview đẹp.

---

## 6. Cách đảm bảo FB preview đẹp

Template `templates/post.html` đã có sẵn:
- `<meta property="og:title">`
- `<meta property="og:description">`
- `<meta property="og:image">` (từ `thumbnail`)
- `<meta property="og:video">` (từ `video_url`, nếu có)
- `<meta property="og:url">` canonical
- `<meta name="twitter:card" content="summary_large_image">`

Sau khi đăng bài, test preview tại: https://developers.facebook.com/tools/debug/ — nếu FB cache sai, bấm **Scrape Again**.

---

## 7. Rate limit

GitHub API cho PAT: **5000 request/giờ**. Với 3-10 bài/ngày, không lo.

---

## 8. Troubleshooting

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `401 Bad credentials` | PAT sai/hết hạn | Tạo PAT mới |
| `403 Forbidden` | PAT thiếu scope `contents:write` | Chỉnh PAT permission |
| `404 Not Found` | Sai repo name | Check `owner/repo` |
| `422 Validation Failed` | JSON sai format | Xem error message chi tiết |
| URL 404 sau 2 phút | Action chưa deploy xong / có lỗi build | Check https://github.com/duckiendlc/cudanhonghot/actions |
