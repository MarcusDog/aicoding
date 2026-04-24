# 用户手册

## 1. 环境要求

- Python 3.11
- 可访问中金所、人民银行、国家统计局公开网页
- Windows 本机环境建议安装浏览器与 Docker Desktop

## 2. 安装依赖

```powershell
python -m pip install -r requirements.txt
```

## 3. 刷新真实数据

```powershell
python scripts/refresh_data.py --days 180
```

如需同时演示 Spark local：

```powershell
python scripts/refresh_data.py --days 180 --enable-spark
```

执行成功后将生成：

- `data/raw/`: 原始抓取文件
- `data/warehouse/`: Parquet 数据集
- `data/futures_analytics.duckdb`: 本地分析数据库

## 4. 一键启动

```powershell
python scripts/run_local_stack.py
```

或：

```powershell
.\start_local.bat
```

启动后访问：

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8501`

## 5. 页面说明

- 答辩展示：系统总览、收益对比、交易所通知、数据质量
- 市场总览：各品种收益与风险概览
- 合约行情：主力连续 K 线、成交量、持仓量、原始合约表
- 趋势与波动：均线、回撤、滚动波动率、未来 5 日波动率预测
- 相关性与风险：VaR、相关性矩阵、预测误差
- 数据来源：数据源说明、质量报告、通知列表

## 6. 主要接口

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

## 7. 论文素材导出

```powershell
python scripts/export_thesis_assets.py
python scripts/capture_app_screenshots.py
```

导出目录：

- `artifacts/thesis/figures/`
- `artifacts/thesis/diagrams/`
- `artifacts/thesis/screenshots/`

## 8. 常见问题

- 页面提示无数据：
  先执行 `python scripts/refresh_data.py --days 180`
- API 能启动但页面为空：
  检查 `GET /api/system/health`，确认状态为 `ready`
- Spark 运行失败：
  不影响主流程，系统默认使用 `Pandas + DuckDB`
- 部分官方源抓取较慢：
  属于正常现象，数据刷新脚本联网阶段耗时会明显高于本地分析阶段
