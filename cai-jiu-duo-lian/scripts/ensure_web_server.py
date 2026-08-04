#!/usr/bin/env python3
"""确保 Web 服务可用：已运行则返回地址，未运行则后台启动。"""
from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
WEB_SERVER = SCRIPTS_DIR / "web_server.py"
DEFAULT_PORT = 8765
DEFAULT_HOST = "127.0.0.1"
HEALTH_PATH = "/api/health"


def _health_url(host: str, port: int) -> str:
    return f"http://{host}:{port}{HEALTH_PATH}"


def _page_url(host: str, port: int) -> str:
    display = "127.0.0.1" if host in ("0.0.0.0", "::") else host
    return f"http://{display}:{port}/"


def is_server_up(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(_health_url(host, port), timeout=timeout) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def start_background(host: str, port: int) -> None:
    env = os.environ.copy()
    env["CAIJIU_WEB_HOST"] = host
    env["CAIJIU_WEB_PORT"] = str(port)
    kwargs: dict = {
        "cwd": str(SCRIPTS_DIR.parent),
        "env": env,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen([sys.executable, str(WEB_SERVER)], **kwargs)


def wait_until_up(host: str, port: int, seconds: float = 15.0) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        if is_server_up(host, port):
            return True
        time.sleep(0.3)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="确保菜就多练 Web 服务运行")
    parser.add_argument("--host", default=os.environ.get("CAIJIU_WEB_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("CAIJIU_WEB_PORT", DEFAULT_PORT)))
    parser.add_argument("--lan", action="store_true", help="绑定 0.0.0.0，允许局域网访问")
    parser.add_argument("--foreground", action="store_true", help="前台运行（不后台守护）")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果")
    args = parser.parse_args()

    host = "0.0.0.0" if args.lan else args.host

    if args.foreground:
        os.environ["CAIJIU_WEB_HOST"] = host
        os.environ["CAIJIU_WEB_PORT"] = str(args.port)
        os.execv(sys.executable, [sys.executable, str(WEB_SERVER)])

    if is_server_up("127.0.0.1", args.port):
        url = _page_url("127.0.0.1", args.port)
        if args.json:
            print(json_dumps({"ok": True, "started": False, "url": url}))
        else:
            print(f"Web 服务已在运行: {url}")
        return

    if _port_in_use(args.port):
        raise SystemExit(
            f"端口 {args.port} 已被占用，且 /api/health 无响应。"
            "请更换端口：CAIJIU_WEB_PORT=8770 python scripts/ensure_web_server.py"
        )

    start_background(host, args.port)
    if not wait_until_up("127.0.0.1", args.port):
        raise SystemExit("Web 服务启动超时，请手动运行: python scripts/web_server.py")

    url = _page_url("127.0.0.1", args.port)
    if args.json:
        print(json_dumps({"ok": True, "started": True, "url": url, "host": host, "port": args.port}))
    else:
        print(f"Web 服务已启动: {url}")
        if host == "0.0.0.0":
            print("局域网访问: 请在本机终端查看 web_server 输出的 IP 地址")


def json_dumps(obj: dict) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


if __name__ == "__main__":
    main()
