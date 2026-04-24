# 基于大数据的上海市二手房价数据分析系统

本项目包含三个部分：

- `backend/`：Django + DRF 后端、管理后台、SQLite/MySQL 兼容配置
- `frontend/`：Vue 3 + Vite + TypeScript + ECharts 前端答辩演示页面
- `data_pipeline/`：真实数据采集与清洗脚本

## 一键准备

```powershell
./start_project.ps1
```

该脚本会：

1. 安装后端依赖
2. 执行数据库迁移
3. 采集真实样例数据
4. 导入样例数据到数据库
5. 启动后端和前端

## 分步命令

### 后端

```powershell
./start_backend.ps1
```

后端地址：

- `http://127.0.0.1:8000/api/overview/`
- `http://127.0.0.1:8000/admin/`

### 前端

```powershell
./start_frontend.ps1
```

前端地址：

- `http://127.0.0.1:5173/overview`

## 数据采集

```powershell
python data_pipeline/run_pipeline.py
backend/.venv/Scripts/python backend/manage.py import_sample_data
```

当前已落地的样例文件：

- `datasets/official_price_indices_sample.csv`
- `datasets/lianjia_listings_sample.csv`
