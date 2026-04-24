# Project Analysis

## Basic Information

- Thesis title: 基于大数据的中国金融期货交易分析系统设计与实现
- Project name: 基于大数据的中国金融期货交易分析系统
- Task book path: `附件4-郭子健18本科毕业论文(设计)开题报告docx(2).docx`
- Project root: `C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\基于大数据的中国金融期货交易分析系统`
- Student metadata inferred from opening report:
  - 学院：数字科学学院
  - 专业：数据科学与大数据技术
  - 学号：202209518
  - 姓名：郭子健
  - 指导教师：马利平

## Topic and Scope

本课题面向中国金融期货市场的盘后分析场景，围绕中金所股指期货 `IF`、`IH`、`IC`、`IM` 构建一套可复现实验、可查询分析、可视化展示、可论文取证的分析系统。系统使用真实公开数据源而非模拟数据，核心目标不是高频实盘交易，而是完成多源数据采集、清洗入仓、风险分析、趋势分析、波动率预测与结果展示的一体化实现。

开题报告中提及的 Lambda 架构、Hadoop、Kafka 等大数据扩展技术，在当前项目中并未完全以分布式集群形态落地；现版本采取 `Pandas + DuckDB + Parquet` 为主、`PySpark local mode` 为辅的可运行原型方案。这一差异需要在论文中如实说明：系统优先保证毕业设计场景下的真实性、稳定性和可交付性，同时保留向更大规模架构演进的接口。

## Project Structure

- Entry points:
  - `scripts/refresh_data.py`：刷新公开数据并写入原始层与数仓层
  - `scripts/run_local_stack.py`：启动本地 API 与 Streamlit 展示界面
  - `api/main.py`：FastAPI 服务入口
  - `app/streamlit_app.py`：论文答辩与系统展示前端入口
- Core modules:
  - `ingest/`：公开数据源抓取与解析
  - `warehouse/`：DuckDB / Parquet 持久化与查询
  - `analysis/`：主力连续、趋势、波动率、相关性与 VaR 计算
  - `api/`：对外查询接口
  - `app/`：前端交互与图表展示
- Database or dataset:
  - 核心表：`contracts`、`futures_daily`、`macro_series`、`notice_events`
  - 衍生表：`main_contract_daily`、`analysis_snapshot`、`volatility_forecast`、`correlation_matrix`、`market_overview`、`quality_report`
- Key business process:
  - 采集 CFFEX 日统计与通知、PBC 金融统计报告、NBS 宏观数据发布
  - 原始页面与 XML 落盘至 `data/raw/`
  - 标准化后写入 DuckDB/Parquet
  - 生成主力连续序列、滚动收益与波动率、EWMA 预测、历史模拟法 VaR、宏观相关性矩阵
  - 经 FastAPI 输出结构化接口，并由 Streamlit 展示结果
- Deploy or run commands:
  - `python -m pip install -r requirements.txt`
  - `python scripts/refresh_data.py --days 180`
  - `python scripts/run_local_stack.py`
  - `uvicorn api.main:app --reload`
  - `streamlit run app/streamlit_app.py`
  - `docker compose up --build`

## Verified Runtime Evidence

- 2026-03-20 本地读取结果显示 DuckDB 中已有 15 张核心或衍生数据表。
- `contracts` 表共 28 条记录，`IF`、`IH`、`IC`、`IM` 各 7 个合约。
- `futures_daily` 表共 912 条记录，四类股指期货各 228 条，时间范围为 2025-12-19 至 2026-03-19。
- `main_contract_daily` 表共 228 条记录，四类品种各 57 条主力连续记录。
- `macro_series` 表共 18 条记录，覆盖 `m2_yoy`、`m1_yoy`、`loan_yoy`、`interbank_rate`、`social_financing_stock_yoy`、`cpi_yoy`、`ppi_yoy`、`industrial_output_yoy` 等指标。
- `quality_report` 显示：
  - `futures_daily` 成功率为 87.6923%，缺失率为 0。
  - `macro_series` 成功率为 100%，缺失率为 0。
  - `notice_events` 成功率为 100%，缺失率为 0。
- `analysis_snapshot` 最新交易日为 2026-03-19，四个品种均给出主力合约、日收益率、20 日波动率、未来 5 日波动率预测与 60 日历史模拟 VaR。
- `pytest -q` 执行结果为 `8 passed in 2.66s`。

## Key Technical Findings

### 1. Data Acquisition

- `ingest/sources/cffex.py` 通过抓取中金所日统计 XML 构造期货日频行情记录，并同步生成合约表、交易日历和通知列表。
- `ingest/sources/pbc.py` 解析中国人民银行“金融统计数据报告”，提取 `M2`、`M1`、贷款同比、同业拆借利率、社融存量同比等宏观金融指标。
- `ingest/sources/nbs.py` 解析国家统计局“数据发布”，提取 `CPI`、`PPI` 与规模以上工业增加值等宏观指标。
- 原始网页与 XML 全部保留到本地原始层，便于论文复核数据来源。

### 2. Warehouse and Data Model

- `warehouse/storage.py` 将 DataFrame 同时写入 Parquet 文件与 DuckDB 表，实现轻量但结构化的数据仓能力。
- 项目采用“原始层 + 标准层 + 分析层”的分层思路，兼顾可追溯性、查询效率与论文展示需要。
- DuckDB 适合作为毕业设计场景中的嵌入式分析数据库，避免部署完整 OLAP 集群的高成本。

### 3. Analysis Logic

- `analysis/metrics.py` 的核心分析能力包括：
  - 按持仓量优先、成交量次之的规则构建主力连续序列；
  - 计算日收益率、5/20/60 日均线、5/20/60 日年化滚动波动率；
  - 基于 EWMA 与短中期波动率组合形成未来 5 日波动率预测；
  - 以历史模拟法计算 95% 置信水平 VaR；
  - 将期货月度收益与宏观指标按月对齐，计算相关性矩阵；
  - 生成总览快照、质量报告与通知摘要。
- 关键公式来源明确，可在论文中展开：
  - 收益率公式；
  - 年化滚动波动率公式；
  - EWMA 波动率递推公式；
  - 历史模拟法 VaR 公式；
  - Pearson 相关系数公式。

### 4. Service and UI

- `api/main.py` 暴露 10 余个查询接口，涵盖系统健康、合约信息、行情、趋势、波动率预测、相关性、VaR、数据源和质量报告。
- `app/streamlit_app.py` 将系统展示分为首页、市场总览、合约行情、趋势与波动、相关性与风险、数据来源六类页面。
- 项目提供论文资产导出与截图脚本：
  - `scripts/export_thesis_assets.py`
  - `scripts/capture_app_screenshots.py`

## Existing Thesis Assets

- Diagrams:
  - `artifacts/thesis/diagrams/fig_3_1_data_model.svg`
  - `artifacts/thesis/diagrams/fig_4_1_system_architecture.svg`
  - `artifacts/thesis/diagrams/fig_4_2_data_flow.svg`
- Figures:
  - `artifacts/thesis/figures/fig_6_1_product_comparison.png`
  - `artifacts/thesis/figures/fig_6_2_if_trend_ma20.png`
  - `artifacts/thesis/figures/fig_6_3_if_drawdown_volatility.png`
  - `artifacts/thesis/figures/fig_6_4_var_bar.png`
  - `artifacts/thesis/figures/fig_6_5_correlation_heatmap.png`
  - `artifacts/thesis/figures/fig_6_6_quality_overview.png`
- Screenshots:
  - `artifacts/thesis/screenshots/fig_5_1_defense_dashboard.png`
  - `artifacts/thesis/screenshots/fig_5_2_market_page_if.png`
  - `artifacts/thesis/screenshots/fig_5_3_trend_page_if.png`
  - `artifacts/thesis/screenshots/fig_5_4_risk_page.png`
  - `artifacts/thesis/screenshots/fig_5_5_source_page.png`

## Evidence To Collect

- Screenshots:
  - 已具备 5 张系统截图，分辨率均为 `2000x1225`
- Figures or charts:
  - 已具备 6 张结果图和 3 张结构图
- Tables:
  - 功能需求表
  - 数据源与数据表设计表
  - 测试用例与结果表
  - 关键指标结果表
- Core code excerpts:
  - CFFEX 日统计解析
  - 波动率预测逻辑
  - API 路由实现
- Formulas:
  - 收益率
  - 年化波动率
  - EWMA
  - 历史模拟 VaR
  - Pearson 相关系数
- Test results:
  - 单元测试通过
  - 数据质量统计
  - 最新分析快照

## Risks and Mitigation

- Missing task book: 无，已从开题报告提取研究内容、进度与预期成果。
- Missing screenshots: 无，现有截图可直接嵌入论文。
- Missing metrics: 主要指标已提取，但当前宏观样本月份较少，相关性分析需要在论文中说明样本窗口有限。
- Missing real references: 需全部改用已核验的真实文献和官方数据源，不能沿用开题报告中未经核实的条目。
- Template fidelity risk: 模板前置页为往届样例，必须仅替换变量字段，不重建封面和目录骨架。
