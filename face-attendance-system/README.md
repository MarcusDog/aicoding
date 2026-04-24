# 人脸识别考勤签到系统

基于 `Flask + Vue3 + 微信小程序` 的考勤系统，包含：

- 人脸注册、人脸签到、GPS 半径校验
- 管理端用户管理、规则配置、考勤统计、报表导出
- 模型阈值校准、投影头训练脚本
- Docker 一键部署与演示数据填充

## 目录结构

- `backend/` 后端 API、数据模型、核心算法
- `admin-web/` 管理员 Web（Vue3）
- `miniprogram/` 微信小程序
- `scripts/` 初始化、数据库优化、演示数据、模型训练脚本
- `docs/` API/部署/数据库/模型与真机测试文档

## 本地启动

1. 安装后端依赖并启动

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

2. 初始化数据库与管理员

```bash
cd ..
python scripts/init_db.py
python scripts/db_optimize.py
```

默认管理员：

- `username`: `admin`
- `password`: `admin123`

3. 填充演示数据

```bash
python scripts/seed_data.py --clear --users 120 --days 45
```

4. 启动管理端

```bash
cd admin-web
npm install
npm run dev
```

## 模型训练与阈值校准

1. 下载 LFW 子集并转换为训练目录
2. 训练投影头（PCA + LDA）
3. 重新标定匹配阈值

```bash
cd scripts/model
python train_pipeline.py
```

输出：

- `models/facenet/projection_head.npz`
- `models/facenet/threshold.json`

训练后如需启用，请在 `backend/.env` 中配置：

```env
FACE_PROJECTION_PATH=../models/facenet/projection_head.npz
FACE_THRESHOLD_PATH=../models/facenet/threshold.json
```

## Docker 部署

```bash
docker compose up --build -d
```

访问地址：

- 统一入口（Nginx）：`http://localhost`
- API 健康检查：`http://localhost/health`

## 微信小程序真机说明

- 在 `miniprogram/config/index.js` 把 `dev.baseURL` 改成你电脑局域网 IP，例如 `http://192.168.1.20:5000/api`
- 确保手机和电脑同一 Wi-Fi
- 后端放行 5000 端口
- 详细步骤见 `docs/miniprogram_real_device.md`

## 测试

```bash
cd backend
python -m pytest -q
```

接口冒烟：

```bash
python scripts/smoke_test.py --base-url http://localhost:5000/api
```
