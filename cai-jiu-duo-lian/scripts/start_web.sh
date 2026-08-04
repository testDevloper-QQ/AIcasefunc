#!/usr/bin/env sh
# 启动菜就多练 Web 服务（自动检测 Python）
set -e
cd "$(dirname "$0")/.."

LAN=0
PORT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --lan|-Lan) LAN=1 ;;
    --port) PORT="$2"; shift ;;
  esac
  shift
done

if [ -n "$CAIJIU_PYTHON" ] && [ -x "$CAIJIU_PYTHON" ]; then
  PYTHON="$CAIJIU_PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "未找到 Python。请安装 Python 3.10+ 或设置 CAIJIU_PYTHON" >&2
  exit 1
fi

ARGS="scripts/ensure_web_server.py --foreground"
[ "$LAN" = 1 ] && ARGS="$ARGS --lan"
[ -n "$PORT" ] && ARGS="$ARGS --port $PORT"

echo "启动菜就多练 Web 服务..."
exec $PYTHON $ARGS
