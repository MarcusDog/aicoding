#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if command -v python3.11 >/dev/null 2>&1; then
  exec python3.11 deploy_start.py "$@"
fi

if command -v python3.10 >/dev/null 2>&1; then
  exec python3.10 deploy_start.py "$@"
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 deploy_start.py "$@"
fi

echo "未检测到 Python 3.10+。请先安装 Python 3.11 后重试。"
exit 1
