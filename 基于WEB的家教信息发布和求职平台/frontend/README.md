# 前端说明

当前前端为 Vue 3 + Vue Router 架构，不使用 Vite 开发服务器，最终由 Spring Boot 托管静态资源。

## 源码位置

- `frontend/src/main.js`
- `frontend/src/api.js`
- `frontend/src/store.js`
- `frontend/src/helpers.js`
- `frontend/src/styles.css`

## 同步到后端静态目录

```bash
npm install
npm run sync
```

同步后会写入：

- `backend/src/main/resources/static/index.html`
- `backend/src/main/resources/static/app/*`
- `backend/src/main/resources/static/vendor/*`

## 启动项目

```bash
./scripts/start_backend.sh
```

浏览器访问：

```text
http://localhost:8080/
```
