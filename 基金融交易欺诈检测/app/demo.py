from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fraud_detection.inference import feature_schema, load_bundle, predict_records  # noqa: E402
from fraud_detection.settings import FIGURES_DIR, METRICS_DIR, MODELS_DIR, SCREENSHOTS_DIR, STREAMING_DIR  # noqa: E402
from fraud_detection.streaming import load_stream_outputs  # noqa: E402


st.set_page_config(page_title="金融交易欺诈检测答辩看板", layout="wide")
st.title("金融交易欺诈检测答辩看板")
st.caption("离线模型评估 + Kafka/Spark 准实时风险识别 + 论文配图导出")

metrics_path = METRICS_DIR / "best_metrics.json"
predictions_path = METRICS_DIR / "test_predictions.csv"
model_path = MODELS_DIR / "best_model.joblib"
training_summary_path = METRICS_DIR / "training_summary.json"

if not model_path.exists():
    st.warning("尚未训练模型，请先运行 scripts/train_model.py")
    st.stop()

bundle = load_bundle(model_path)
schema = feature_schema(bundle)
metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
training_summary = json.loads(training_summary_path.read_text(encoding="utf-8")) if training_summary_path.exists() else {}
stream_frame, stream_summary = load_stream_outputs(STREAMING_DIR)

header_cols = st.columns(5)
header_cols[0].metric("最佳模型", bundle["model_name"])
header_cols[1].metric("PR-AUC", f"{metrics.get('pr_auc', 0):.4f}")
header_cols[2].metric("Recall", f"{metrics.get('recall', 0):.4f}")
header_cols[3].metric("FPR", f"{metrics.get('fpr', 0):.4f}")
header_cols[4].metric("阈值", f"{bundle['threshold']:.6f}")

tab_overview, tab_predict, tab_stream, tab_assets = st.tabs(
    ["系统概览", "离线预测", "准实时监控", "论文配图与截图"]
)

with tab_overview:
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("项目摘要")
        st.markdown(
            """
            - 真实主数据源：OpenML `creditcard`，共 284,807 条交易记录。
            - 核心目标：在极度不平衡场景下提高欺诈召回能力，同时控制误报率。
            - 技术路线：离线训练、阈值优化、Kafka 消息队列、Spark Structured Streaming 微批打分。
            - 当前最佳方案：LightGBM 离线模型，准实时链路用于演示实时风险识别流程。
            """
        )
        st.subheader("运行摘要")
        st.json(training_summary)
        st.subheader("接口样例")
        st.code(
            json.dumps({"transaction_id": "demo-001", "features": schema["sample_features"]}, indent=2, ensure_ascii=False),
            language="json",
        )
    with right:
        st.subheader("关键图表")
        for image_name in ["best_model_pr_curve.png", "best_model_threshold_tradeoff.png"]:
            image_path = FIGURES_DIR / image_name
            if image_path.exists():
                st.image(str(image_path), caption=image_name, use_container_width=True)

with tab_predict:
    st.subheader("离线样例预测")
    left, right = st.columns([1, 1.1])
    if predictions_path.exists():
        prediction_frame = pd.read_csv(predictions_path)
        row_index = left.number_input("选择测试集样本行号", min_value=0, max_value=len(prediction_frame) - 1, value=0)
        sample = prediction_frame.iloc[int(row_index)].to_dict()
        feature_payload = {key: float(sample[key]) for key in bundle["feature_columns"]}
        result = predict_records(bundle, [{"transaction_id": f"sample_{row_index}", **feature_payload}])[0]
        left.json(result)
        right.dataframe(
            pd.DataFrame([feature_payload]).T.rename(columns={0: "value"}),
            use_container_width=True,
            height=620,
        )
    else:
        st.info("未找到测试集预测结果。")

    st.divider()
    st.subheader("批量 CSV 预测")
    upload = st.file_uploader("上传包含完整特征列的 CSV 文件", type=["csv"])
    if upload is not None:
        upload_frame = pd.read_csv(upload)
        results = predict_records(bundle, upload_frame.to_dict(orient="records"))
        result_frame = pd.DataFrame(results)
        st.dataframe(result_frame, use_container_width=True)
        st.download_button(
            "下载批量预测结果",
            data=result_frame.to_csv(index=False).encode("utf-8-sig"),
            file_name="defense_batch_predictions.csv",
            mime="text/csv",
        )

with tab_stream:
    top = st.columns(4)
    top[0].metric("最近批次", stream_summary.get("batch_id", "-"))
    top[1].metric("批次事件数", stream_summary.get("event_count", 0))
    top[2].metric("高风险命中", stream_summary.get("high_risk_count", 0))
    top[3].metric("平均风险分", f"{stream_summary.get('average_score', 0):.4f}")

    st.markdown(
        """
        **演示链路**
        `Kafka Producer -> Kafka Topic -> Spark Structured Streaming -> 模型打分 -> 实时结果落盘 -> Streamlit 看板`
        """
    )
    st.code(
        ".\\.venv\\Scripts\\python scripts\\setup_kafka.py start\n"
        ".\\.venv\\Scripts\\python scripts\\run_streaming_job.py\n"
        ".\\.venv\\Scripts\\python scripts\\replay_to_kafka.py --rows 300 --delay 0.05",
        language="powershell",
    )

    if not stream_frame.empty:
        chart_cols = st.columns([1.4, 1])
        with chart_cols[0]:
            view = stream_frame[["transaction_id", "fraud_score", "risk_level"]].tail(50).reset_index(drop=True)
            st.line_chart(view.set_index("transaction_id")[["fraud_score"]], height=260)
        with chart_cols[1]:
            risk_counts = stream_frame["risk_level"].value_counts().rename_axis("risk_level").reset_index(name="count")
            st.bar_chart(risk_counts.set_index("risk_level"))
        st.dataframe(stream_frame.tail(30), use_container_width=True, height=320)
    else:
        st.info("暂无流式结果，请先启动 Kafka / Spark / 回放脚本。")

with tab_assets:
    st.subheader("论文配图与截图资源")
    st.markdown(
        """
        - 本页展示的图表与页面截图均可直接用于论文“系统实现”和“实验结果分析”章节。
        - 建议截图顺序：系统概览页、离线预测页、准实时监控页。
        - 建议配图顺序：系统总体架构图、离线实验对比图、阈值权衡图、实时链路架构图、监控看板截图。
        """
    )
    asset_paths = []
    for directory in [FIGURES_DIR, SCREENSHOTS_DIR]:
        if directory.exists():
            for path in sorted(directory.glob("*")):
                asset_paths.append(path)

    if asset_paths:
        selected = st.selectbox("选择资源预览", asset_paths, format_func=lambda path: path.name)
        if selected.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            st.image(str(selected), caption=selected.name, use_container_width=True)
        else:
            st.code(selected.read_text(encoding="utf-8"), language="markdown")
    else:
        st.info("当前还没有生成论文截图资源。")
