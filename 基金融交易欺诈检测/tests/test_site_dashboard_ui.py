from fraud_detection.site_ui import get_primary_nav_items


def test_get_primary_nav_items_returns_web_nav():
    items = get_primary_nav_items()

    assert items == [
        {"label": "驾驶舱", "page": "dashboard"},
        {"label": "风险案例", "page": "cases"},
        {"label": "模型效果", "page": "metrics"},
    ]
