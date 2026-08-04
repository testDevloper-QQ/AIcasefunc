#!/usr/bin/env python3
"""菜就多练 Web 服务：静态页面 + /api/recommend Skill 推荐 API。"""
from __future__ import annotations

import json
import mimetypes
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from recommend_engine import recommend  # noqa: E402
from skill_loader import get_skill_root, load_config  # noqa: E402

HOST = "0.0.0.0"
PORT = 8765


def local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


class Handler(BaseHTTPRequestHandler):
    skill_root: Path
    skill_meta: dict

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def _send_json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            self._send_json(200, {"ok": True, "service": "菜就多练"})
            return

        if path == "/api/config":
            cfg = load_config()
            self._send_json(200, {"config": cfg, "skill": self.skill_meta})
            return

        if path == "/api/skill/refresh":
            try:
                self.skill_root, self.skill_meta = get_skill_root(force_refresh=True)
                self._send_json(200, {"ok": True, "skill": self.skill_meta})
            except Exception as exc:
                self._send_json(500, {"ok": False, "error": str(exc)})
            return

        if path.startswith("/skill-assets/"):
            rel = path[len("/skill-assets/") :]
            file_path = (self.skill_root / rel).resolve()
            if not str(file_path).startswith(str(self.skill_root.resolve())):
                self.send_error(403)
                return
            if file_path.is_file():
                self._serve_file(file_path)
                return
            self.send_error(404)
            return

        if path == "/":
            path = "/index.html"
        file_path = (WEB_DIR / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(WEB_DIR.resolve())):
            self.send_error(403)
            return
        if file_path.is_file():
            self._serve_file(file_path)
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/recommend":
            self.send_error(404)
            return
        try:
            data = self._read_json_body()
            ingredients = data.get("ingredients") or []
            if not ingredients:
                self._send_json(400, {"error": "请至少选择一种食材"})
                return
            result = recommend(
                self.skill_root,
                scene=data.get("scene") or None,
                ingredients=ingredients,
                taste=(data.get("taste") or "").strip(),
                servings_label=(data.get("servings") or "").strip(),
                free_text=(data.get("freeText") or "").strip(),
            )
            self._send_json(200, {"ok": True, "skill": self.skill_meta, **result})
        except Exception as exc:
            self._send_json(500, {"ok": False, "error": str(exc)})

    def _serve_file(self, file_path: Path) -> None:
        ctype, _ = mimetypes.guess_type(str(file_path))
        ctype = ctype or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if file_path.suffix == ".html":
            self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    skill_root, skill_meta = get_skill_root()
    Handler.skill_root = skill_root
    Handler.skill_meta = skill_meta

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    ip = local_ip()
    print("=" * 50)
    print("菜就多练 Web 服务已启动")
    print(f"  本机访问: http://127.0.0.1:{PORT}/")
    print(f"  手机访问: http://{ip}:{PORT}/  （需同一 WiFi）")
    print(f"  Skill 来源: {skill_meta.get('source')} → {skill_meta.get('skillRoot')}")
    if skill_meta.get("source") == "git":
        print(f"  Git 仓库: {skill_meta.get('gitRepoUrl')}")
        print(f"  菜谱索引: {skill_meta.get('recipeCount')} 条")
        print("  刷新远程 Skill: GET /api/skill/refresh")
    print("  添加到手机桌面: 浏览器菜单 → 添加到主屏幕")
    print("=" * 50)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        server.server_close()


if __name__ == "__main__":
    main()
