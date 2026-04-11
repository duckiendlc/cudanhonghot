// Banner aff logic chỉ chạy trên trang bài viết
(function () {
  const overlay = document.getElementById("banner-overlay");
  if (!overlay) return;

  const closeBtn = document.getElementById("banner-close");
  const link = document.getElementById("banner-link");
  const affUrl = window.AFF_URL;

  // Lock scroll khi banner hiện
  document.body.style.overflow = "hidden";

  function dismiss(openAff) {
    overlay.classList.add("hidden");
    document.body.style.overflow = "";
    if (openAff && affUrl) {
      window.open(affUrl, "_blank", "noopener");
    }
  }

  closeBtn.addEventListener("click", (e) => {
    e.preventDefault();
    dismiss(true);
  });

  // Bấm vào ảnh banner: browser tự mở link (target=_blank), ta chỉ đóng overlay
  link.addEventListener("click", () => dismiss(false));

  // ESC = coi như bấm X (mở aff)
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") dismiss(true);
  });
})();
