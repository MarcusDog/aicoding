from __future__ import annotations

import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fraud_detection.site_content import (  # noqa: E402
    build_cases_content,
    build_dashboard_content,
    build_metrics_content,
    build_primary_nav_items,
)
from fraud_detection.site_presenter import (  # noqa: E402
    build_case_frame,
    build_dashboard_frame,
    build_dashboard_summary,
)
from fraud_detection.site_runtime import load_site_state  # noqa: E402
from fraud_detection.site_ui import (  # noqa: E402
    inject_site_css,
    render_hero,
    render_page_intro,
    render_primary_topbar,
    render_section_title,
    render_summary_card,
)


st.set_page_config(page_title="金融交易风险驾驶舱", layout="wide", initial_sidebar_state="collapsed")
inject_site_css()


def _current_page() -> str:
    current = st.query_params.get("page", "dashboard")
    if isinstance(current, list):
        current = current[0]
    valid_pages = {item["page"] for item in build_primary_nav_items()}
    return current if current in valid_pages else "dashboard"


def _rename_columns(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = frame.rename(
        columns={
            "transaction_id": "交易编号",
            "source": "数据来源",
            "risk_index": "风险指数",
            "display_risk_level": "风险等级",
            "fraud_score": "模型分数",
            "actual_label": "真实标签",
            "predicted_positive": "模型预警",
            "reason_display": "风险解释",
        }
    )
    if "模型分数" in renamed.columns:
        renamed["模型分数"] = renamed["模型分数"].map(lambda value: f"{float(value):.6f}")
    return renamed


def _risk_trend_chart(frame: pd.DataFrame):
    chart_data = frame.reset_index(drop=True).copy()
    chart_data["序号"] = chart_data.index + 1
    return (
        alt.Chart(chart_data)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("序号:Q", title="样本序号"),
            y=alt.Y("risk_index:Q", title="风险指数", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color(
                "display_risk_level:N",
                title="风险等级",
                scale=alt.Scale(domain=["low", "medium", "high"], range=["#93c5fd", "#38bdf8", "#1d4ed8"]),
            ),
            tooltip=[
                alt.Tooltip("transaction_id:N", title="交易编号"),
                alt.Tooltip("risk_index:Q", title="风险指数"),
                alt.Tooltip("display_risk_level:N", title="风险等级"),
            ],
        )
        .properties(height=320)
    )


def _risk_distribution_chart(frame: pd.DataFrame):
    distribution = (
        frame["display_risk_level"]
        .value_counts()
        .rename_axis("风险等级")
        .reset_index(name="数量")
    )
    return (
        alt.Chart(distribution)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("风险等级:N", sort=["low", "medium", "high"]),
            y=alt.Y("数量:Q"),
            color=alt.Color(
                "风险等级:N",
                scale=alt.Scale(domain=["low", "medium", "high"], range=["#93c5fd", "#38bdf8", "#1d4ed8"]),
                legend=None,
            ),
            tooltip=["风险等级:N", "数量:Q"],
        )
        .properties(height=320)
    )


def _render_dashboard(state) -> None:
    dashboard_frame = build_dashboard_frame(state.stream_frame, state.prediction_frame)
    summary = build_dashboard_summary(dashboard_frame, batch_id=state.stream_summary.get("batch_id"))
    content = build_dashboard_content(state.metrics, summary)

    render_hero(content["hero"]["title"], content["hero"]["description"], content["hero"]["meta"])

    render_section_title("风险总览")
    summary_cols = st.columns(4)
    for column, item in zip(summary_cols, content["summary_cards"]):
        with column:
            render_summary_card(item["label"], item["value"])

    render_section_title("风险走势")
    if not dashboard_frame.empty:
        chart_cols = st.columns([1.3, 1])
        with chart_cols[0]:
            st.altair_chart(_risk_trend_chart(dashboard_frame), use_container_width=True)
        with chart_cols[1]:
            st.altair_chart(_risk_distribution_chart(dashboard_frame), use_container_width=True)
    else:
        st.info("当前暂无可展示的风险数据。")

    render_section_title(content["table_title"])
    if not dashboard_frame.empty:
        table_frame = _rename_columns(
            dashboard_frame[
                ["transaction_id", "source", "risk_index", "display_risk_level", "fraud_score", "reason_display"]
            ]
        )
        st.dataframe(table_frame, width="stretch", height=360, hide_index=True)
    else:
        st.info("暂无最近风险记录。")


def _render_cases(state) -> None:
    content = build_cases_content()
    case_frame = build_case_frame(state.stream_frame, state.prediction_frame, state.bundle, limit=24)
    render_page_intro(content["title"], content["description"])

    if case_frame.empty:
        st.info("当前没有可展示的风险案例。")
        return

    summary_cols = st.columns(4)
    metrics = [
        ("案例总数", str(len(case_frame))),
        ("高风险案例", str(int((case_frame["display_risk_level"] == "high").sum()))),
        ("模型预警", str(int(case_frame["predicted_positive"].sum()))),
        ("最高风险指数", f"{case_frame['risk_index'].max():.1f}"),
    ]
    for column, item in zip(summary_cols, metrics):
        with column:
            render_summary_card(item[0], item[1])

    render_section_title("高风险样本列表")
    table_frame = _rename_columns(
        case_frame[
            [
                "transaction_id",
                "source",
                "risk_index",
                "display_risk_level",
                "fraud_score",
                "actual_label",
                "predicted_positive",
                "reason_display",
            ]
        ]
    )
    st.dataframe(table_frame, width="stretch", height=520, hide_index=True)


def _render_metrics(state) -> None:
    content = build_metrics_content(state.metrics)
    render_page_intro(content["title"], content["description"], content["meta"])

    metric_cards = [
        ("PR-AUC", f"{state.metrics.get('pr_auc', 0):.4f}"),
        ("Recall", f"{state.metrics.get('recall', 0):.4f}"),
        ("FPR", f"{state.metrics.get('fpr', 0):.4f}"),
        ("Threshold", f"{state.metrics.get('threshold', 0):.6f}"),
    ]
    metric_cols = st.columns(4)
    for column, item in zip(metric_cols, metric_cards):
        with column:
            render_summary_card(item[0], item[1])

    figures = [
        PROJECT_ROOT / "artifacts" / "figures" / "best_model_pr_curve.png",
        PROJECT_ROOT / "artifacts" / "figures" / "best_model_threshold_tradeoff.png",
        PROJECT_ROOT / "artifacts" / "figures" / "best_model_confusion_matrix.png",
    ]
    render_section_title("实验图表")
    image_cols = st.columns(2)
    for index, figure_path in enumerate(figures[:2]):
        with image_cols[index]:
            if figure_path.exists():
                st.image(str(figure_path), use_container_width=True)
    if figures[2].exists():
        st.image(str(figures[2]), use_container_width=True)


try:
    state = load_site_state()
except FileNotFoundError:
    st.warning("尚未训练模型，请先运行 `scripts/train_model.py`。")
    st.stop()

current_page = _current_page()
render_primary_topbar(current_page)

if current_page == "dashboard":
    _render_dashboard(state)
elif current_page == "cases":
    _render_cases(state)
else:
    _render_metrics(state)
