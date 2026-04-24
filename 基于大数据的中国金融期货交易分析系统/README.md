# 基于真实公开数据的中国股指期货盘后分析系统

本项目是一个面向毕业设计场景的可运行原型，聚焦中金所股指期货 `IF`、`IH`、`IC`、`IM`，使用真实且可核验的公开数据完成数据采集、清洗建模、趋势分析、波动率预测、相关性分析、VaR 风险度量与可视化展示。

## 已实现功能

- 中金所 `CFFEX` 官方盘后日统计抓取与标准化
- `PBC` / `NBS` 官方宏观指标抓取
- `DuckDB + Parquet` 本地数仓
- 主力连续序列、趋势分析、回撤、成交量异动识别
- 滚动波动率与未来 5 日波动率预测
- 股指收益与宏观指标相关性分析
- 历史模拟法 `VaR`
- `FastAPI` 查询接口
- `Streamlit` 答辩展示页面
- 论文配图、结构图、系统截图自动导出
- `Docker Compose` 本机部署

## 技术栈

- Python 3.11
- DuckDB / Parquet
- FastAPI
- Streamlit
- PySpark local mode
- Docker Compose

## 快速开始

### 1. 安装依赖

```powershell
python -m pip install -r requirements.txt
```

### 2. 拉取并构建真实数据

```powershell
python scripts/refresh_data.py --days 180
```

如需同时生成 Spark local 演示数据：

```powershell
python scripts/refresh_data.py --days 180 --enable-spark
```

### 3. 一键启动本地系统

```powershell
python scripts/run_local_stack.py
```

Windows 也可以直接双击或执行：

```powershell
.\start_local.bat
```

启动后访问：

- API 文档: `http://127.0.0.1:8000/docs`
- 前端页面: `http://127.0.0.1:8501`

### 4. 手动启动

```powershell
uvicorn api.main:app --reload
streamlit run app/streamlit_app.py
```

### 5. Docker 启动

```powershell
docker compose up --build
```

### 6. 导出论文图表和截图

```powershell
python scripts/export_thesis_assets.py
python scripts/capture_app_screenshots.py
```

输出目录：

- `artifacts/thesis/figures/`
- `artifacts/thesis/diagrams/`
- `artifacts/thesis/screenshots/`

## 目录说明

- `ingest/`: 官方数据源采集器
- `warehouse/`: DuckDB / Parquet 持久化
- `analysis/`: 指标与分析逻辑
- `api/`: FastAPI 接口
- `app/`: Streamlit 前端
- `scripts/`: 数据刷新、启动、截图、配图导出
- `docs/`: 系统设计、数据库设计、用户手册、论文素材说明
- `tests/`: 解析、分析、接口测试

## 主要接口

- `GET /api/system/health`
- `GET /api/contracts`
- `GET /api/market/daily`
- `GET /api/analysis/trend`
- `GET /api/analysis/volatility`
- `GET /api/analysis/volatility-forecast`
- `GET /api/analysis/correlation`
- `GET /api/analysis/overview`
- `GET /api/analysis/comparison`
- `GET /api/analysis/var`
- `GET /api/metadata/sources`
- `GET /api/metadata/quality`
- `GET /api/metadata/notices`

## 与开题报告的对应关系

- 数据采集、存储、处理、分析、可视化模块均已落地
- 趋势分析、波动率预测、相关性分析、VaR 已实现
- 多源公开数据已接入：CFFEX、PBC、NBS
- 本机可运行原型、技术文档、截图素材已具备

说明：

- 由于公开数据授权边界，系统采用“盘后分析”定位，不做未授权实时行情分发
- Hadoop / Kafka / 全分布式集群属于扩展架构说明，当前版本以可运行的本机原型为主
- Spark local 已保留接口，默认主流程使用 Pandas + DuckDB 以保证稳定性
