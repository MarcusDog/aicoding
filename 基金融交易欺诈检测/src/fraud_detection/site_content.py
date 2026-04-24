from __future__ import annotations

from typing import Any


def _format_decimal(value: Any, digits: int = 4) -> str:
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return "-"


def _format_integer(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "-"


def build_primary_nav_items() -> list[dict[str, str]]:
    return [
        {"label": "驾驶舱", "page": "dashboard"},
        {"label": "风险案例", "page": "cases"},
        {"label": "模型效果", "page": "metrics"},
    ]


def build_dashboard_content(metrics: dict[str, Any], dashboard_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "hero": {
            "title": "金融交易风险驾驶舱",
            "description": "展示当前批次的风险指数分布、关键案例和模型识别态势。",
            "meta": f"模型：LightGBM · PR-AUC：{_format_decimal(metrics.get('pr_auc'))}",
        },
        "summary_cards": [
            {"label": "当前批次", "value": str(dashboard_summary.get("batch_id", "-"))},
            {"label": "事件数", "value": _format_integer(dashboard_summary.get("event_count", 0))},
            {"label": "高风险样本", "value": _format_integer(dashboard_summary.get("high_risk_count", 0))},
            {
                "label": "平均风险指数",
                "value": _format_decimal(dashboard_summary.get("average_risk_index", 0), digits=1),
            },
        ],
        "table_title": "最近风险记录",
    }


def build_cases_content() -> dict[str, str]:
    return {
        "title": "风险案例",
        "description": "汇总当前流式批次与离线测试集中的高风险样本，便于老师快速查看典型案例。",
    }


def build_metrics_content(metrics: dict[str, Any]) -> dict[str, str]:
    return {
        "title": "模型效果",
        "description": "展示核心指标、阈值表现与实验图表，直接对应论文实验结果部分。",
        "meta": (
            f"Recall：{_format_decimal(metrics.get('recall'))} · "
            f"FPR：{_format_decimal(metrics.get('fpr'))} · "
            f"Threshold：{_format_decimal(metrics.get('threshold'), digits=6)}"
        ),
    }
