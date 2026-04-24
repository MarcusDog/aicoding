#!/bin/zsh
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
STATIC_DIR="$ROOT_DIR/backend/src/main/resources/static"

if [[ ! -f "$FRONTEND_DIR/node_modules/vue/dist/vue.global.prod.js" ]]; then
  echo "缺少 Vue 运行时依赖，请先在 frontend 目录执行 npm install。" >&2
  exit 1
fi

mkdir -p "$STATIC_DIR/app" "$STATIC_DIR/vendor"

cp "$FRONTEND_DIR/src/"*.js "$STATIC_DIR/app/"
cp "$FRONTEND_DIR/src/styles.css" "$STATIC_DIR/app/styles.css"
cp "$FRONTEND_DIR/node_modules/vue/dist/vue.global.prod.js" "$STATIC_DIR/vendor/vue.global.prod.js"
cp "$FRONTEND_DIR/node_modules/vue-router/dist/vue-router.global.prod.js" "$STATIC_DIR/vendor/vue-router.global.prod.js"

echo "Vue 前端资源已同步到 Spring Boot 静态目录。"
