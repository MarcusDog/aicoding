from fraud_detection.site_content import build_dashboard_content, build_primary_nav_items


def test_build_primary_nav_items_exposes_three_pages():
    assert build_primary_nav_items() == [
        {"label": "驾驶舱", "page": "dashboard"},
        {"label": "风险案例", "page": "cases"},
        {"label": "模型效果", "page": "metrics"},
    ]


def test_build_dashboard_content_exposes_compact_sections():
    content = build_dashboard_content(
        metrics={"pr_auc": 0.77},
        dashboard_summary={"batch_id": 4, "event_count": 30, "high_risk_count": 6, "average_risk_index": 58.4},
    )

    assert content["hero"]["title"] == "金融交易风险驾驶舱"
    assert len(content["summary_cards"]) == 4
    assert content["table_title"] == "最近风险记录"


def test_build_dashboard_content_formats_summary_cards():
    content = build_dashboard_content(
        metrics={"pr_auc": 0.7729},
        dashboard_summary={"batch_id": 4, "event_count": 30, "high_risk_count": 2, "average_risk_index": 51.23},
    )

    metric_map = {item["label"]: item["value"] for item in content["summary_cards"]}
    assert metric_map["当前批次"] == "4"
    assert metric_map["事件数"] == "30"
    assert metric_map["高风险样本"] == "2"
    assert metric_map["平均风险指数"] == "51.2"
