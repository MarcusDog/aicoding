from __future__ import annotations

import math
import os
from typing import Any

import numpy as np
import pandas as pd

from .amap_client import AmapClient


def minmax(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    min_val = float(series.min())
    max_val = float(series.max())
    if math.isclose(min_val, max_val):
        return pd.Series([0.5] * len(series), index=series.index, dtype=float)
    return (series - min_val) / (max_val - min_val)


def haversine_meters(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    radius = 6371000
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def grid_id_for_point(lon: float, lat: float, cell_size_m: int = 250) -> str:
    origin_lon = 121.48
    origin_lat = 31.25
    meters_per_lon = 111320 * math.cos(math.radians(lat))
    meters_per_lat = 110540
    x = int(((lon - origin_lon) * meters_per_lon) // cell_size_m)
    y = int(((lat - origin_lat) * meters_per_lat) // cell_size_m)
    return f"YANGPU_{x}_{y}"


def _activity_hint(source: str) -> float:
    source = str(source).lower()
    if any(token in source for token in ["metro", "subway", "station"]):
        return 1.0
    if any(token in source for token in ["mall", "market", "commercial"]):
        return 0.8
    if any(token in source for token in ["campus", "university", "school"]):
        return 0.7
    return 0.5


def maybe_enrich_candidate_points(points: pd.DataFrame, amap: AmapClient | None) -> pd.DataFrame:
    out = points.copy()
    if "poi_score" not in out.columns:
        out["poi_score"] = np.nan
    poi_enrich_enabled = os.getenv("ENABLE_AMAP_POI_ENRICH", "0").strip() == "1"
    if amap is None or not poi_enrich_enabled:
        out["poi_score"] = out["poi_score"].fillna(out["source"].map(_activity_hint))
        return out

    keywords = ["地铁站", "商场", "学校", "办公楼", "小吃", "夜市"]
    for idx, row in out.iterrows():
        if pd.notna(row.get("poi_score")):
            continue
        try:
            count = amap.poi_count(float(row["lon"]), float(row["lat"]), keywords=keywords, radius=500)
        except Exception:
            count = None
        if count is not None:
            out.at[idx, "poi_score"] = count
    out["poi_score"] = out["poi_score"].fillna(out["source"].map(_activity_hint))
    return out


def build_hotspots(complaints: pd.DataFrame) -> pd.DataFrame:
    located = complaints[complaints["is_located"]].copy()
    if located.empty:
        return pd.DataFrame(columns=["grid_id", "lon", "lat", "complaint_count"])
    located["grid_id"] = [
        grid_id_for_point(float(lon), float(lat)) for lon, lat in zip(located["lon"], located["lat"])
    ]
    hotspots = (
        located.groupby("grid_id", as_index=False)
        .agg(
            complaint_count=("id", "count"),
            lon=("lon", "mean"),
            lat=("lat", "mean"),
            latest_created_at=("created_at", "max"),
        )
        .sort_values("complaint_count", ascending=False)
    )
    hotspots["hotspot_score"] = minmax(hotspots["complaint_count"].astype(float))
    return hotspots


def build_point_features(
    complaints: pd.DataFrame,
    candidate_points: pd.DataFrame,
    calendar: pd.DataFrame,
    weather: pd.DataFrame,
    flow_observation: pd.DataFrame | None = None,
) -> pd.DataFrame:
    points = candidate_points.copy()
    points["grid_id"] = [grid_id_for_point(float(lon), float(lat)) for lon, lat in zip(points["lon"], points["lat"])]

    calendar_map = calendar.set_index("date") if not calendar.empty else pd.DataFrame()
    weather_map = weather.set_index("date") if not weather.empty else pd.DataFrame()

    complaints = complaints.copy()
    if not complaints.empty:
        complaints["date"] = complaints["date"].astype(str)
        if not calendar_map.empty:
            complaints = complaints.join(calendar_map[["is_holiday", "is_weekend"]], on="date", rsuffix="_calendar")
        else:
            complaints["is_holiday"] = 0
            complaints["is_weekend"] = complaints["created_at"].dt.weekday.ge(5).astype(int)

        if not weather_map.empty:
            complaints = complaints.join(weather_map[["weather_code", "weather_text"]], on="date", rsuffix="_weather")
        else:
            complaints["weather_code"] = np.nan
            complaints["weather_text"] = ""

    feature_rows: list[dict[str, Any]] = []
    located = complaints[complaints["is_located"]].copy() if not complaints.empty else complaints.copy()
    rainy_codes = {51, 53, 55, 61, 63, 65, 71, 73, 75, 80, 81, 82, 95, 96, 99}

    for _, point in points.iterrows():
        if not located.empty:
            distances = [
                haversine_meters(float(point["lon"]), float(point["lat"]), float(row["lon"]), float(row["lat"]))
                for _, row in located.iterrows()
            ]
            nearby = located.assign(distance_m=distances)
        else:
            nearby = pd.DataFrame(columns=list(located.columns) + ["distance_m"])

        within_250 = nearby[nearby["distance_m"] <= 250]
        within_500 = nearby[nearby["distance_m"] <= 500]

        total_250 = int(len(within_250))
        total_500 = int(len(within_500))
        oil_ratio = (
            float(
                (
                    within_500["category"].astype(str).str.contains("油烟|餐饮", regex=True, na=False)
                    | within_500["content"].astype(str).str.contains("油烟|餐饮", regex=True, na=False)
                ).mean()
            )
            if total_500
            else 0.0
        )
        road_ratio = (
            float(
                (
                    within_500["category"].astype(str).str.contains("占道|道路|流动摊", regex=True, na=False)
                    | within_500["content"].astype(str).str.contains("占道|道路|流动摊", regex=True, na=False)
                ).mean()
            )
            if total_500
            else 0.0
        )
        night_ratio = float(within_500["hour_bucket"].astype(float).ge(18).mean()) if total_500 else 0.0
        weekend_ratio = float(within_500["is_weekend"].fillna(0).astype(float).mean()) if total_500 else 0.0
        holiday_ratio = float(within_500["is_holiday"].fillna(0).astype(float).mean()) if total_500 else 0.0
        bad_weather_ratio = (
            float(pd.to_numeric(within_500["weather_code"], errors="coerce").isin(rainy_codes).mean()) if total_500 else 0.0
        )

        feature_rows.append(
            {
                "point_id": point["point_id"],
                "point_name": point["point_name"],
                "grid_id": point["grid_id"],
                "lon": point["lon"],
                "lat": point["lat"],
                "source": point["source"],
                "label": point.get("label"),
                "label_source": point.get("label_source"),
                "complaint_count_250m": total_250,
                "complaint_count_500m": total_500,
                "oil_smoke_ratio": oil_ratio,
                "road_occupation_ratio": road_ratio,
                "night_complaint_ratio": night_ratio,
                "weekend_complaint_ratio": weekend_ratio,
                "holiday_complaint_ratio": holiday_ratio,
                "bad_weather_ratio": bad_weather_ratio,
                "poi_score_raw": point.get("poi_score", np.nan),
            }
        )

    features = pd.DataFrame(feature_rows)
    if features.empty:
        return features

    if flow_observation is not None and not flow_observation.empty:
        flow = flow_observation.copy()
        flow["flow_proxy_score"] = pd.to_numeric(flow["flow_proxy_score"], errors="coerce")
        flow_agg = flow.groupby("point_id", as_index=False)["flow_proxy_score"].mean()
        features = features.merge(flow_agg, on="point_id", how="left")
    else:
        features["flow_proxy_score"] = np.nan

    features["poi_score_raw"] = pd.to_numeric(features["poi_score_raw"], errors="coerce")
    features["flow_proxy_score"] = pd.to_numeric(features["flow_proxy_score"], errors="coerce")
    features["poi_score"] = minmax(features["poi_score_raw"].fillna(features["source"].map(_activity_hint)))
    features["flow_proxy_score"] = features["flow_proxy_score"].fillna(features["poi_score"])
    features["flow_proxy_score"] = minmax(features["flow_proxy_score"])

    complaint_risk_raw = (
        features["complaint_count_250m"] * 0.7
        + features["complaint_count_500m"] * 0.3
        + features["oil_smoke_ratio"] * 3
        + features["road_occupation_ratio"] * 2
    )
    features["complaint_risk"] = minmax(complaint_risk_raw)
    features["activity_proxy"] = minmax(features["flow_proxy_score"] * 0.6 + features["poi_score"] * 0.4)
    features["date"] = pd.Timestamp.utcnow().date().isoformat()
    features["hour_bucket"] = -1
    features["risk_level"] = pd.cut(
        features["complaint_risk"],
        bins=[-0.01, 0.33, 0.66, 1.0],
        labels=["low", "medium", "high"],
    ).astype(str)
    return features
