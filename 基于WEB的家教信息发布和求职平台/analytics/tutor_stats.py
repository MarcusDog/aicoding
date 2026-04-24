from collections import Counter


def _count_by(items, key):
    return dict(Counter(item.get(key, "UNKNOWN") for item in items))


def build_summary(data):
    """Build platform operation indicators from exported backend records."""
    users = data.get("users", [])
    demands = data.get("demands", [])
    applications = data.get("applications", [])
    orders = data.get("orders", [])

    app_counts = _count_by(applications, "status")
    total_applications = sum(app_counts.values())
    accepted = app_counts.get("ACCEPTED", 0)
    conversion_rate = accepted / total_applications if total_applications else 0

    return {
        "roles": _count_by(users, "role"),
        "demands": _count_by(demands, "status"),
        "applications": app_counts,
        "orders": _count_by(orders, "status"),
        "application_conversion_rate": round(conversion_rate, 4),
    }


def recommend_actions(summary):
    """Return concise operation notes for the admin dashboard and thesis analysis."""
    actions = []
    if summary.get("demands", {}).get("PENDING_REVIEW", 0) > 0:
        actions.append("存在待审核需求，建议管理员优先完成审核以提升需求流转速度。")
    if summary.get("applications", {}).get("SUBMITTED", 0) > 0:
        actions.append("存在待处理接单申请，建议及时确认合适教员并生成订单。")
    if summary.get("application_conversion_rate", 0) < 0.3:
        actions.append("申请转化率偏低，建议优化需求描述、预算范围和教员推荐策略。")
    if not actions:
        actions.append("平台当前运行状态稳定，可继续观察新增需求与订单完成情况。")
    return actions


if __name__ == "__main__":
    demo_data = {
        "users": [{"role": "PARENT"}, {"role": "TUTOR"}, {"role": "ADMIN"}],
        "demands": [{"status": "OPEN"}, {"status": "PENDING_REVIEW"}],
        "applications": [{"status": "SUBMITTED"}],
        "orders": [{"status": "ACTIVE"}],
    }
    summary = build_summary(demo_data)
    print(summary)
    for action in recommend_actions(summary):
        print("-", action)
