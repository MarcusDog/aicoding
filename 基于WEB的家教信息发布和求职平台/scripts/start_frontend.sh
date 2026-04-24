#!/bin/zsh
set -e

"$(dirname "$0")/sync_frontend.sh"
echo "Vue 前端资源已同步。请运行 ./scripts/start_backend.sh，然后访问 http://localhost:8080/"
