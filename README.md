# MYBLOG - Web đơn giản có banner affiliate

Web tĩnh siêu nhẹ: trang chủ chỉ có logo + danh sách bài, mỗi bài bị chặn bởi banner affiliate, bấm X → mở link aff + hiện nội dung.

## Chạy

Mở trực tiếp `index.html` bằng trình duyệt, hoặc chạy server tĩnh:

```bash
# Python
python -m http.server 8000

# Node
npx serve .
```

## Cấu hình

### 1. Link affiliate & banner — `config.js`
```js
const CONFIG = {
  affiliateUrl: "https://link-aff-cua-ban.com",
  bannerImage: "https://url-anh-banner.jpg",  // hoặc "images/banner.jpg"
  siteName: "MYBLOG"
};
```

### 2. Thêm bài viết — `posts.js`
Thêm object mới vào mảng `POSTS`:
```js
{
  id: "ten-bai-khong-dau",
  title: "Tiêu đề bài",
  date: "2026-04-11",
  content: `
    <h1>Tiêu đề</h1>
    <p>Nội dung...</p>
    <img src="https://..." alt="" />
    <iframe src="https://www.youtube.com/embed/VIDEO_ID"></iframe>
    <video src="videos/clip.mp4" controls></video>
  `
}
```

### 3. Logo
Sửa trong `index.html`, tìm `<h1 class="logo">MY<span>BLOG</span></h1>`.

## Cấu trúc

```
WEB/
├── index.html    # HTML chính
├── styles.css    # Giao diện
├── app.js        # Router + logic banner
├── config.js     # Link aff + ảnh banner
├── posts.js      # Danh sách bài viết
└── README.md
```

## Cách hoạt động

1. **Home** (`#/`) — Chỉ logo + danh sách link bài viết.
2. **Đọc bài** (`#/post/:id`) — Banner overlay hiện ngay, chặn nội dung.
3. **Bấm X** — Mở tab mới đến link affiliate, banner biến mất, lộ nội dung.
