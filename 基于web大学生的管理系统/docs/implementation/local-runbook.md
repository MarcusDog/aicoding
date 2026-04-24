# 本机运行说明

## 1. 启动顺序

1. 执行 `scripts/init-db.ps1` 可重置本地 H2 数据库
2. 执行 `scripts/start-backend.ps1` 启动后端，默认端口 `8080`
3. 执行 `scripts/start-frontend.ps1` 启动前端，默认端口 `5173`

## 2. 默认账号

- 管理员：`A1001` / `123456`
- 学生：`202209501` / `123456`

## 3. 访问地址

- 前端页面：`http://localhost:5173`
- 后端接口：`http://localhost:8080/api`
- H2 控制台：`http://localhost:8080/h2-console`

## 4. 当前技术口径

- 前端：Vue 3 + Vite + Element Plus
- 后端：Spring Boot + MyBatis-Plus
- 本地数据库：H2 MySQL 模式
- 数据脚本：根目录 `database/` 与后端资源 `backend/src/main/resources/sql/`
