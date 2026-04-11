// Danh sách bài viết
// Thêm bài mới bằng cách thêm object vào mảng POSTS
// content hỗ trợ HTML: <p>, <h2>, <img>, <video>, <iframe> (YouTube)

const POSTS = [
  {
    id: "bai-viet-dau-tien",
    title: "Bài viết đầu tiên",
    date: "2026-04-11",
    content: `
      <h1>Bài viết đầu tiên</h1>
      <div class="meta">Đăng ngày 11/04/2026</div>

      <p>Đây là đoạn mở đầu của bài viết. Bạn có thể viết nội dung tự do bằng HTML.</p>

      <h2>Chèn hình ảnh</h2>
      <p>Ví dụ chèn ảnh từ URL:</p>
      <img src="https://picsum.photos/800/450" alt="Ảnh minh họa" />

      <h2>Chèn video YouTube</h2>
      <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" frameborder="0" allowfullscreen></iframe>

      <h2>Video trực tiếp từ link</h2>
      <video src="https://cdn.videy.co/e6vInmF01.mp4" controls playsinline preload="metadata"></video>

      <p>Kết thúc bài viết. Cảm ơn bạn đã đọc!</p>
    `
  },
  {
    id: "bai-viet-thu-hai",
    title: "Bài viết thứ hai - Hướng dẫn sử dụng",
    date: "2026-04-10",
    content: `
      <h1>Hướng dẫn sử dụng</h1>
      <div class="meta">Đăng ngày 10/04/2026</div>

      <p>Để thêm bài viết mới, mở file <code>posts.js</code> và thêm một object vào mảng <code>POSTS</code>.</p>

      <h2>Cấu trúc bài viết</h2>
      <p>Mỗi bài cần: <strong>id</strong> (không dấu, dùng dấu gạch ngang), <strong>title</strong>, <strong>date</strong>, và <strong>content</strong> (HTML).</p>

      <img src="https://picsum.photos/800/400?random=2" alt="Minh họa" />

      <p>Rất đơn giản!</p>
    `
  }
];
