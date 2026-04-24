from __future__ import annotations

import numpy as np
import pandas as pd


RULE_WEIGHTS = {
    "activity_component": 0.30,
    "flow_component": 0.20,
    "temporal_component": 0.12,
    "stability_component": 0.08,
    "low_complaint_component": 0.20,
    "street_friendly_component": 0.10,
}


def minmax(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    values = pd.to_numeric(series, errors="coerce")
    min_val = values.min(skipna=True)
    max_val = values.max(skipna=True)
    if pd.isna(min_val) or pd.isna(max_val) or abs(max_val - min_val) < 1e-9:
        return pd.Series(np.full(len(values), 0.5), index=series.index)
    return (values - min_val) / (max_val - min_val)


def _safe_numeric(out: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for col in columns:
        if col not in out.columns:
            out[col] = 0.0
        out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
    return out


def build_rule_score(features: pd.DataFrame) -> pd.DataFrame:
    out = features.copy()
    out = _safe_numeric(
        out,
        [
            "complaint_risk",
            "activity_proxy",
            "flow_proxy_score",
            "weekend_complaint_ratio",
            "holiday_complaint_ratio",
            "bad_weather_ratio",
            "road_occupation_ratio",
            "poi_score",
        ],
    )

    temporal_opportunity = minmax(out["weekend_complaint_ratio"] + out["holiday_complaint_ratio"])
    weather_stability = 1 - minmax(out["bad_weather_ratio"])
    low_complaint = 1 - minmax(out["complaint_risk"])
    street_friendly = 1 - minmax(out["road_occupation_ratio"])
    activity_component = RULE_WEIGHTS["activity_component"] * minmax(out["activity_proxy"])
    flow_component = RULE_WEIGHTS["flow_component"] * minmax(out["flow_proxy_score"])
    temporal_component = RULE_WEIGHTS["temporal_component"] * temporal_opportunity
    stability_component = RULE_WEIGHTS["stability_component"] * weather_stability
    low_complaint_component = RULE_WEIGHTS["low_complaint_component"] * low_complaint
    street_friendly_component = RULE_WEIGHTS["street_friendly_component"] * street_friendly

    out["activity_component"] = activity_component
    out["flow_component"] = flow_component
    out["temporal_component"] = temporal_component
    out["stability_component"] = stability_component
    out["low_complaint_component"] = low_complaint_component
    out["street_friendly_component"] = street_friendly_component
    out["temporal_opportunity"] = temporal_opportunity
    out["weather_stability"] = weather_stability
    out["street_friendly_score"] = street_friendly
    out["low_complaint_score"] = low_complaint
    out["rule_score"] = (
        activity_component
        + flow_component
        + temporal_component
        + stability_component
        + low_complaint_component
        + street_friendly_component
    )
    return out


def _top_reasons(row: pd.Series) -> tuple[str, str]:
    positive_components = {
        "活动活跃度强": float(row.get("activity_component", 0.0)),
        "流量代理较强": float(row.get("flow_component", 0.0)),
        "节假日/周末机会更高": float(row.get("temporal_component", 0.0)),
        "天气稳定性较好": float(row.get("stability_component", 0.0)),
        "投诉压力较低": float(row.get("low_complaint_component", 0.0)),
        "道路占压风险较低": float(row.get("street_friendly_component", 0.0)),
    }
    sorted_positive = sorted(positive_components.items(), key=lambda item: item[1], reverse=True)
    reason_1 = sorted_positive[0][0] if sorted_positive else "综合表现均衡"

    complaint_risk = float(row.get("complaint_risk", 0.0))
    road_risk = float(row.get("road_occupation_ratio", 0.0))
    if complaint_risk >= 0.66:
        reason_2 = "投诉压力偏高"
    elif road_risk >= 0.50:
        reason_2 = "道路占压问题需重点关注"
    else:
        reason_2 = sorted_positive[1][0] if len(sorted_positive) > 1 else "综合表现均衡"
    return reason_1, reason_2


def build_explanations(scored: pd.DataFrame) -> pd.DataFrame:
    out = scored.copy()
    reason_1: list[str] = []
    reason_2: list[str] = []
    explanation: list[str] = []
    primary_component: list[str] = []

    for _, row in out.iterrows():
        r1, r2 = _top_reasons(row)
        primary_component.append(r1)
        reason_1.append(r1)
        reason_2.append(r2)
        explanation.append(f"{r1}，{r2}")

    out["primary_component"] = primary_component
    out["reason_1"] = reason_1
    out["reason_2"] = reason_2
    out["explanation_text"] = explanation
    out["risk_level"] = pd.cut(
        pd.to_numeric(out["complaint_risk"], errors="coerce").fillna(0.0),
        bins=[-0.01, 0.33, 0.66, 1.0],
        labels=["low", "medium", "high"],
    ).astype(str)
    return out
