# 部署文档

## 1. Docker Compose 部署

```bash
docker compose up --build -d
```

服务说明：

- `mysql`：MySQL 8
- `redis`：限流与缓存
- `backend`：Flask + Gunicorn
- `admin-web`：Vue 静态站点
- `nginx`：统一网关（`/` 前端、`/api` 后端）

访问：

- `http://localhost`（管理端）
- `http://localhost/health`（后端健康检查）

## 2. 初始化

```bash
python scripts/init_db.py
python scripts/db_optimize.py
python scripts/seed_data.py --clear
```

## 3. 关键环境变量（backend）

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `SECRET_KEY`
- `RATE_LIMIT_STORAGE_URI`
- `WECHAT_LOGIN_MODE`
- `WECHAT_APPID`
- `WECHAT_SECRET`
- `FACE_MATCH_THRESHOLD`
- `FACE_PROJECTION_PATH`
- `FACE_THRESHOLD_PATH`

## 4. 生产建议

- `WECHAT_LOGIN_MODE=real` 并配置真实小程序 `APPID/SECRET`
- 启用 HTTPS（Nginx + 证书）
- 上传目录挂载对象存储或 NAS
- 周期性备份 MySQL 与模型配置文件
