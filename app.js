// Router tối giản dùng hash (#/ và #/post/:id)

const homeView = document.getElementById("home");
const postView = document.getElementById("post");
const postContent = document.getElementById("post-content");
const postListEl = document.getElementById("post-list");

const overlay = document.getElementById("banner-overlay");
const bannerImage = document.getElementById("banner-image");
const bannerLink = document.getElementById("banner-link");
const bannerClose = document.getElementById("banner-close");

// Render danh sách bài trên home
function renderPostList() {
  postListEl.innerHTML = POSTS.map(p => `
    <li>
      <a href="#/post/${p.id}">
        ${escapeHtml(p.title)}
        <span class="date">${escapeHtml(p.date || "")}</span>
      </a>
    </li>
  `).join("");
}

function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

// Hiện banner affiliate MỖI LẦN vào bài
// UX: click X hoặc click banner đều mở aff + đóng banner. ESC cũng được.
let bannerOpen = false;

function showBanner() {
  bannerImage.src = CONFIG.bannerImage;
  bannerLink.href = CONFIG.affiliateUrl;
  overlay.classList.remove("hidden");
  document.body.style.overflow = "hidden";
  bannerOpen = true;
}

function hideBannerAndOpenAff(e) {
  if (!bannerOpen) return;
  if (e) e.preventDefault();
  bannerOpen = false;
  overlay.classList.add("hidden");
  document.body.style.overflow = "";
  // Mở link affiliate trong tab mới (user vẫn đang ở trang đọc bài)
  window.open(CONFIG.affiliateUrl, "_blank", "noopener");
}

// Bấm X
bannerClose.addEventListener("click", hideBannerAndOpenAff);
// Bấm vào ảnh banner (thẻ <a>) cũng đóng + mở aff (browser tự mở link, ta đóng overlay)
bannerLink.addEventListener("click", () => {
  bannerOpen = false;
  overlay.classList.add("hidden");
  document.body.style.overflow = "";
});
// Phím ESC
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") hideBannerAndOpenAff(e);
});

// Router
function route() {
  const hash = location.hash || "#/";
  const match = hash.match(/^#\/post\/(.+)$/);

  if (match) {
    const post = POSTS.find(p => p.id === match[1]);
    if (!post) {
      location.hash = "#/";
      return;
    }
    postContent.innerHTML = post.content;
    homeView.classList.add("hidden");
    postView.classList.remove("hidden");
    window.scrollTo(0, 0);
    showBanner();
  } else {
    homeView.classList.remove("hidden");
    postView.classList.add("hidden");
    overlay.classList.add("hidden");
    document.body.style.overflow = "";
  }
}

window.addEventListener("hashchange", route);
renderPostList();
route();
