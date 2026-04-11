"""Bot client - Python SDK đăng bài lên Cư Dân Hóng Hớt.

Dùng GitHub REST API làm backend. Không cần cài thêm thư viện ngoài `requests`.

Cài:
    pip install requests

Sử dụng:
    from bot_client import HongHotClient

    client = HongHotClient(
        repo="duckiendlc/cudanhonghot",
        token="ghp_xxxxxxxxxxxx",  # PAT với scope contents:write
        site_url="https://cudanhonghot.online",
    )

    result = client.create_post(
        title="Tiêu đề giật tít drama",
        content_html="<p>Nội dung bài...</p>",
        thumbnail="https://example.com/thumb.jpg",
        video_url="https://cdn.videy.co/abc.mp4",
        description="Tóm tắt 1-2 câu cho FB preview",
        categories=["Drama"],
        tags=["nong", "hot"],
        source_url="https://honghotduong.com/bai-goc",
    )

    print(result["post_url"])   # https://cudanhonghot.online/post/20260411-xxx/
    print(result["post_id"])    # 20260411-xxx
    print(result["build_url"])  # link Actions để theo dõi deploy

Lưu ý:
- Sau create_post, GitHub Action tự build & deploy ~30-60s.
- URL được return NGAY, nhưng có thể 404 trong ~1 phút đầu cho tới khi deploy xong.
- Nếu bot muốn chắc chắn live: poll post_url cho tới khi status 200.
"""

from __future__ import annotations

import base64
import json
import re
import unicodedata
from datetime import datetime
from typing import Any

import requests

GITHUB_API = "https://api.github.com"


def slugify(text: str) -> str:
    """Bỏ dấu tiếng Việt, chuyển sang kebab-case, chỉ giữ [a-z0-9-]."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "d")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:80] or "untitled"


class HongHotClient:
    def __init__(self, repo: str, token: str, site_url: str, branch: str = "main"):
        """
        repo      : "owner/repo" ví dụ "duckiendlc/cudanhonghot"
        token     : GitHub Personal Access Token (scope: contents:write)
        site_url  : URL public của site, ví dụ "https://cudanhonghot.online"
        branch    : branch để commit, mặc định "main"
        """
        self.repo = repo
        self.token = token
        self.site_url = site_url.rstrip("/")
        self.branch = branch
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })

    # ------------ public API ------------

    def create_post(
        self,
        title: str,
        content_html: str,
        thumbnail: str = "",
        video_url: str = "",
        description: str = "",
        categories: list[str] | None = None,
        tags: list[str] | None = None,
        source_url: str = "",
        slug: str | None = None,
        date: str | None = None,
    ) -> dict[str, Any]:
        """Tạo bài viết mới. Trả về dict có post_url, post_id, build_url.

        Raises:
            ValueError  : input không hợp lệ
            RuntimeError: GitHub API trả lỗi
        """
        if not title or not content_html:
            raise ValueError("title và content_html bắt buộc")

        date = date or datetime.now().strftime("%Y-%m-%d")
        base_slug = slug or slugify(title)
        post_id = f"{date.replace('-', '')}-{base_slug}"

        # Tránh trùng: thêm suffix nếu file đã tồn tại
        post_id = self._uniquify(post_id)

        payload = {
            "title": title,
            "date": date,
            "description": description or title,
            "thumbnail": thumbnail,
            "video_url": video_url,
            "categories": categories or [],
            "tags": tags or [],
            "source_url": source_url,
            "content_html": content_html,
        }

        path = f"posts/{post_id}.json"
        self._put_file(
            path=path,
            content=json.dumps(payload, ensure_ascii=False, indent=2),
            message=f"post: {title[:60]}",
        )

        return {
            "post_id": post_id,
            "post_url": f"{self.site_url}/post/{post_id}/",
            "build_url": f"https://github.com/{self.repo}/actions",
            "raw_path": path,
        }

    def delete_post(self, post_id: str) -> None:
        """Xóa bài viết theo post_id (slug không có .json)."""
        path = f"posts/{post_id}.json"
        info = self._get_file(path)
        if not info:
            raise RuntimeError(f"Không tìm thấy {path}")
        self._delete_file(path, sha=info["sha"], message=f"delete: {post_id}")

    def list_posts(self) -> list[str]:
        """List tất cả post_id hiện có."""
        url = f"{GITHUB_API}/repos/{self.repo}/contents/posts"
        r = self.session.get(url, params={"ref": self.branch})
        if r.status_code == 404:
            return []
        r.raise_for_status()
        return [
            item["name"].removesuffix(".json")
            for item in r.json()
            if item["name"].endswith(".json")
        ]

    # ------------ internal ------------

    def _uniquify(self, post_id: str) -> str:
        existing = set(self.list_posts())
        if post_id not in existing:
            return post_id
        i = 2
        while f"{post_id}-{i}" in existing:
            i += 1
        return f"{post_id}-{i}"

    def _get_file(self, path: str) -> dict | None:
        url = f"{GITHUB_API}/repos/{self.repo}/contents/{path}"
        r = self.session.get(url, params={"ref": self.branch})
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()

    def _put_file(self, path: str, content: str, message: str) -> None:
        url = f"{GITHUB_API}/repos/{self.repo}/contents/{path}"
        body = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "branch": self.branch,
        }
        existing = self._get_file(path)
        if existing:
            body["sha"] = existing["sha"]
        r = self.session.put(url, json=body)
        if r.status_code not in (200, 201):
            raise RuntimeError(f"GitHub API {r.status_code}: {r.text}")

    def _delete_file(self, path: str, sha: str, message: str) -> None:
        url = f"{GITHUB_API}/repos/{self.repo}/contents/{path}"
        body = {"message": message, "sha": sha, "branch": self.branch}
        r = self.session.delete(url, json=body)
        if r.status_code != 200:
            raise RuntimeError(f"GitHub API {r.status_code}: {r.text}")
