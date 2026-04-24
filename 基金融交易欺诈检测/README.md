# 金融交易欺诈检测

本项目基于真实公开交易数据完成极度不平衡场景下的金融交易欺诈检测，包含：

- 真实数据下载脚本
- 数据切分与防泄漏处理
- 多模型与多策略实验
- 阈值优化与核心指标评估
- 本地 API 服务
- Streamlit 演示页面

## 已选数据源

- 主数据集：OpenML `creditcard`（对应 Dal Pozzolo 等人公开的真实信用卡交易欺诈数据）
- 扩展数据集：SEC Form N-MFP 官方数据（月度货币基金申报数据）

## 快速开始

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python scripts\download_datasets.py --download-sec-nmfp
.venv\Scripts\python scripts\train_model.py --max-train-rows 120000
.venv\Scripts\python scripts\run_api.py
.venv\Scripts\streamlit run app\demo.py
```

## 网站展示页

```powershell
.\.venv\Scripts\python scripts\start_site.py --port 8520
```

- 默认网站地址：`http://127.0.0.1:8520`
- 当前网站为单页驾驶舱展示，不包含侧边栏和多页面入口

## 训练模式

- 快速本地迭代：`.\.venv\Scripts\python scripts\train_model.py --max-train-rows 120000`
- 完整实验：`.\.venv\Scripts\python scripts\train_model.py --full`

## API

- `GET /health`
- `GET /metrics`
- `GET /schema`
- `POST /predict`
- `POST /predict/batch`

## 答辩版启动

```powershell
.\.venv\Scripts\python scripts\start_defense_stack.py
.\.venv\Scripts\python scripts\run_stream_demo.py
.\.venv\Scripts\python scripts\check_system.py
```

- 一键准备答辩资产：`.\.venv\Scripts\python scripts\prepare_defense_assets.py`
- 单独刷新看板截图：`.\.venv\Scripts\python scripts\capture_dashboard_screenshots.py`
- 默认 API：`http://127.0.0.1:8000`
- 默认答辩看板：`http://127.0.0.1:8512`
- Kafka 对 WSL/Spark 通告地址：`172.27.128.1:9092`

## 关键输出

- `data/raw/creditcard.csv`
- `data/external/sec/`
- `artifacts/metrics/experiment_results.csv`
- `artifacts/metrics/best_metrics.json`
- `models/best_model.joblib`
- `artifacts/figures/`

## 数据来源

- Dal Pozzolo A, et al. *Learned lessons in credit card fraud detection from a practitioner perspective*, 2014
- OpenML: <https://www.openml.org/>
- SEC Form N-MFP: <https://www.sec.gov/data-research/sec-markets-data/dera-form-n-mfp-data-sets>
