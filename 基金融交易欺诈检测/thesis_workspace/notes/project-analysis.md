# Project Analysis

## Basic Information

- Thesis title: 基于LightGBM的金融交易欺诈检测系统设计与实现
- Project name: 基金融交易欺诈检测
- Task book path: `C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\基金融交易欺诈检测\附件4-本科毕业论文(设计)开题报告202510.docx`
- Project root: `C:\Users\lenovo\OneDrive\Desktop\毕业设计_4\基金融交易欺诈检测`

## Project Structure

- Entry points:
  - `scripts/train_model.py` 负责离线训练与实验对比。
  - `scripts/run_api.py` 负责启动 FastAPI 推理服务。
  - `app/demo.py` 负责启动 Streamlit 答辩看板。
  - `scripts/run_streaming_job.py` 与 `scripts/replay_to_kafka.py` 负责准实时演示链路。
- Core modules:
  - `src/fraud_detection/data.py` 负责真实数据下载与加载。
  - `src/fraud_detection/preprocess.py` 负责时序切分与采样器构造。
  - `src/fraud_detection/modeling.py` 负责实验配置与模型训练。
  - `src/fraud_detection/evaluation.py` 负责指标计算、阈值优化与图表导出。
  - `src/fraud_detection/inference.py` 负责模型加载、批量预测和风险解释。
  - `src/fraud_detection/streaming.py` 负责流式结果持久化与汇总。
- Dataset:
  - OpenML `creditcard` 数据集，284807 条交易，492 条欺诈样本，欺诈比例约 0.1727%。
- Key business process:
  - 真实数据下载 -> 数据切分 -> 多模型训练 -> 验证集阈值优化 -> 最优模型落盘 -> FastAPI 服务推理 -> Streamlit 页面展示 -> Kafka/Spark 准实时演示。
- Deploy or run commands:
  - `.venv\Scripts\python scripts\train_model.py --max-train-rows 120000`
  - `.venv\Scripts\python scripts\run_api.py`
  - `.venv\Scripts\streamlit run app\demo.py`
  - `.venv\Scripts\python scripts\start_defense_stack.py`

## Evidence To Collect

- Screenshots:
  - `artifacts/screenshots/defense_overview.png`
  - `artifacts/screenshots/defense_offline_prediction.png`
  - `artifacts/screenshots/defense_streaming_monitor.png`
- Figures or charts:
  - `artifacts/figures/thesis_system_architecture.png`
  - `artifacts/figures/thesis_streaming_architecture.png`
  - `artifacts/figures/thesis_model_comparison.png`
  - `artifacts/figures/best_model_pr_curve.png`
  - `artifacts/figures/best_model_threshold_tradeoff.png`
  - `artifacts/figures/best_model_confusion_matrix.png`
  - `artifacts/figures/best_model_feature_importance.png`
- Tables:
  - 需求分析表
  - 数据集基本信息表
  - 数据切分结果表
  - API 接口设计表
  - 模型对比结果表
  - 功能测试结果表
- Core code excerpts:
  - 固定误报率约束下的阈值搜索函数
  - FastAPI 单笔预测接口
  - Spark 微批评分回调函数
- Formulas:
  - Precision
  - Recall
  - FPR
- Test results:
  - `artifacts/metrics/experiment_results.csv`
  - `artifacts/metrics/best_metrics.json`
  - `artifacts/metrics/feature_importance.csv`
  - `artifacts/streaming/latest_summary.json`
  - `tests/test_api.py`
  - `tests/test_evaluation.py`

## Risks

- Missing task book: 已由开题报告替代，正文需以真实项目实现为准，不直接照抄开题报告承诺内容。
- Missing screenshots: 截图已存在，但仍需在最终稿中校验清晰度与标题编号。
- Missing metrics: 主要指标文件齐全，可支撑实验分析。
- Missing real references: 开题报告参考文献中个别条目存在核验风险，最终论文已改为逐条核验后再使用。
- Missing supervisor name: 开题报告中的指导教师字段为空，封面暂保持空白，待用户补充后可重建最终稿。
