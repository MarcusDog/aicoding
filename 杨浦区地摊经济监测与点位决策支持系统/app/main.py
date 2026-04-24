from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import folium
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from folium.plugins import HeatMap
from streamlit_folium import st_folium

from src.model.labeling import (
    build_label_template,
    label_summary,
    manual_labels_path,
    merge_manual_labels,
    read_manual_labels,
    save_manual_labels,
)
from src.model.predict import predict
from src.model.train import train_model
from src.pipeline.io_utils import artifacts_dir, write_csv, write_json


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data"
RAW_ROOT = DATA_ROOT / "raw"
PROCESSED_ROOT = DATA_ROOT / "processed"
EVIDENCE_ROOT = ROOT / "evidence" / "sources"
FIGURE_ROOT = ROOT / "evidence" / "figures"
SCREENSHOT_ROOT = ROOT / "evidence" / "screenshots"


@dataclass
class DataBundle:
    complaints: pd.DataFrame
    candidates: pd.DataFrame
    features: pd.DataFrame
    predictions: pd.DataFrame
    sources: dict[str, str]
    demo_mode: bool


def _existing_path(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if path.exists() and path.is_file() and path.stat().st_size > 0:
            return path
    return None


def _read_csv(paths: Iterable[Path]) -> tuple[pd.DataFrame, str]:
    path = _existing_path(paths)
    if path is None:
        return pd.DataFrame(), "missing"
    try:
        return pd.read_csv(path), str(path)
    except Exception as exc:  # noqa: BLE001
        st.warning(f"读取失败: {path.name} ({exc})")
        return pd.DataFrame(), f"error:{path}"


def _lower_map(columns: Iterable[str]) -> dict[str, str]:
    return {str(col).strip().lower(): str(col) for col in columns}


def _pick_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    if df.empty:
        return None
    lookup = _lower_map(df.columns)
    for name in candidates:
        if name.lower().strip() in lookup:
            return lookup[name.lower().strip()]
    return None


def _coerce_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def _standardize_complaints(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()
    alias_map = {
        "id": ["id", "complaint_id", "record_id"],
        "created_at": ["created_at", "time", "timestamp", "date", "createdtime"],
        "category": ["category", "type", "theme", "subject", "issue_type"],
        "content": ["content", "text", "description", "detail", "complaint_text"],
        "address": ["address", "location", "addr", "site"],
        "lon": ["lon", "lng", "longitude", "x"],
        "lat": ["lat", "latitude", "y"],
    }
    rename: dict[str, str] = {}
    for target, names in alias_map.items():
        picked = _pick_column(out, names)
        if picked and picked != target:
            rename[picked] = target
    out = out.rename(columns=rename)

    if "id" not in out.columns:
        out["id"] = np.arange(1, len(out) + 1)
    if "category" not in out.columns:
        out["category"] = "未分类"
    if "content" not in out.columns:
        out["content"] = ""
    if "address" not in out.columns:
        out["address"] = ""
    if "created_at" not in out.columns:
        out["created_at"] = pd.NaT

    out["created_at"] = pd.to_datetime(out["created_at"], errors="coerce")
    out = _coerce_numeric(out, ["lon", "lat"])
    out["category"] = out["category"].fillna("未分类").astype(str).str.strip()
    out["content"] = out["content"].fillna("").astype(str).str.strip()
    out["address"] = out["address"].fillna("").astype(str).str.strip()
    out["is_located"] = out["lon"].notna() & out["lat"].notna()
    return out.reset_index(drop=True)


def _standardize_candidates(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    out = df.copy()
    alias_map = {
        "point_id": ["point_id", "id", "candidate_id"],
        "point_name": ["point_name", "name", "spot_name", "place_name"],
        "lon": ["lon", "lng", "longitude", "x"],
        "lat": ["lat", "latitude", "y"],
        "source": ["source", "origin", "type", "category"],
    }
    rename: dict[str, str] = {}
    for target, names in alias_map.items():
        picked = _pick_column(out, names)
        if picked and picked != target:
            rename[picked] = target
    out = out.rename(columns=rename)

    if "point_id" not in out.columns:
        out["point_id"] = [f"point-{idx + 1:03d}" for idx in range(len(out))]
    if "point_name" not in out.columns:
        out["point_name"] = out["point_id"].astype(str)
    if "source" not in out.columns:
        out["source"] = "unknown"

    out = _coerce_numeric(out, ["lon", "lat", "poi_score"])
    out["point_name"] = out["point_name"].fillna("未命名点位").astype(str).str.strip()
    out["source"] = out["source"].fillna("unknown").astype(str).str.strip()
    return out.reset_index(drop=True)


def _standardize_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "date" in out.columns:
        out["date"] = pd.to_datetime(out["date"], errors="coerce")
    numeric_columns = [
        "lon",
        "lat",
        "complaint_count_250m",
        "complaint_count_500m",
        "oil_smoke_ratio",
        "road_occupation_ratio",
        "night_complaint_ratio",
        "weekend_complaint_ratio",
        "holiday_complaint_ratio",
        "bad_weather_ratio",
        "poi_score",
        "flow_proxy_score",
        "complaint_risk",
        "activity_proxy",
    ]
    return _coerce_numeric(out, numeric_columns)


def _standardize_predictions(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = _coerce_numeric(df.copy(), ["lon", "lat", "score", "rank", "complaint_risk", "activity_proxy", "flow_proxy_score"])
    text_columns = ["point_id", "point_name", "source", "reason_1", "reason_2", "risk_level", "explanation_text", "grid_id"]
    for col in text_columns:
        if col in out.columns:
            out[col] = out[col].fillna("").astype(str)
    return out


def _demo_bundle() -> DataBundle:
    candidates = pd.DataFrame(
        [
            {"point_id": "demo-1", "point_name": "五角场商圈", "lon": 121.5130, "lat": 31.2990, "source": "mall"},
            {"point_id": "demo-2", "point_name": "同济大学周边", "lon": 121.5065, "lat": 31.2925, "source": "university"},
            {"point_id": "demo-3", "point_name": "江湾体育场", "lon": 121.5125, "lat": 31.3200, "source": "transit"},
        ]
    )
    complaints = pd.DataFrame(
        [
            {
                "id": "demo-c1",
                "created_at": pd.Timestamp("2025-10-01 18:20:00"),
                "category": "占道经营",
                "content": "晚间占道经营影响通行。",
                "address": "五角场商圈",
                "lon": 121.5121,
                "lat": 31.2984,
                "is_located": True,
            },
            {
                "id": "demo-c2",
                "created_at": pd.Timestamp("2025-10-03 20:10:00"),
                "category": "油烟扰民",
                "content": "夜间餐饮油烟扰民。",
                "address": "同济大学周边",
                "lon": 121.5058,
                "lat": 31.2918,
                "is_located": True,
            },
        ]
    )
    features = pd.DataFrame(
        [
            {
                "point_id": "demo-1",
                "point_name": "五角场商圈",
                "grid_id": "YANGPU_DEMO_1",
                "lon": 121.5130,
                "lat": 31.2990,
                "source": "mall",
                "complaint_risk": 0.20,
                "activity_proxy": 0.92,
                "flow_proxy_score": 0.88,
            },
            {
                "point_id": "demo-2",
                "point_name": "同济大学周边",
                "grid_id": "YANGPU_DEMO_2",
                "lon": 121.5065,
                "lat": 31.2925,
                "source": "university",
                "complaint_risk": 0.30,
                "activity_proxy": 0.80,
                "flow_proxy_score": 0.76,
            },
            {
                "point_id": "demo-3",
                "point_name": "江湾体育场",
                "grid_id": "YANGPU_DEMO_3",
                "lon": 121.5125,
                "lat": 31.3200,
                "source": "transit",
                "complaint_risk": 0.15,
                "activity_proxy": 0.86,
                "flow_proxy_score": 0.90,
            },
        ]
    )
    predictions = pd.DataFrame(
        [
            {
                "grid_id": "YANGPU_DEMO_1",
                "point_id": "demo-1",
                "point_name": "五角场商圈",
                "lon": 121.5130,
                "lat": 31.2990,
                "source": "mall",
                "score": 0.90,
                "rank": 1,
                "complaint_risk": 0.20,
                "activity_proxy": 0.92,
                "flow_proxy_score": 0.88,
                "reason_1": "活动代理分较高",
                "reason_2": "投诉风险较低",
                "risk_level": "low",
                "explanation_text": "活动代理分较高，投诉风险较低",
            },
            {
                "grid_id": "YANGPU_DEMO_3",
                "point_id": "demo-3",
                "point_name": "江湾体育场",
                "lon": 121.5125,
                "lat": 31.3200,
                "source": "transit",
                "score": 0.84,
                "rank": 2,
                "complaint_risk": 0.15,
                "activity_proxy": 0.86,
                "flow_proxy_score": 0.90,
                "reason_1": "活动代理分较高",
                "reason_2": "流量代理较强",
                "risk_level": "low",
                "explanation_text": "活动代理分较高，流量代理较强",
            },
        ]
    )
    return DataBundle(
        complaints=complaints,
        candidates=candidates,
        features=features,
        predictions=predictions,
        sources={"complaints": "demo", "candidates": "demo", "features": "demo", "predictions": "demo"},
        demo_mode=True,
    )


@st.cache_data(show_spinner=False)
def load_bundle() -> DataBundle:
    complaints, complaints_src = _read_csv([PROCESSED_ROOT / "complaints_cleaned.csv", RAW_ROOT / "complaints.csv"])
    candidates, candidates_src = _read_csv([PROCESSED_ROOT / "candidate_points_cleaned.csv", RAW_ROOT / "candidate_points.csv"])
    features, features_src = _read_csv([PROCESSED_ROOT / "features.csv"])
    predictions, predictions_src = _read_csv([PROCESSED_ROOT / "predictions.csv"])

    if complaints.empty and candidates.empty and features.empty and predictions.empty:
        return _demo_bundle()

    return DataBundle(
        complaints=_standardize_complaints(complaints),
        candidates=_standardize_candidates(candidates),
        features=_standardize_features(features),
        predictions=_standardize_predictions(predictions),
        sources={
            "complaints": complaints_src,
            "candidates": candidates_src,
            "features": features_src,
            "predictions": predictions_src,
        },
        demo_mode=False,
    )


def _normalize(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    if values.empty:
        return values
    minimum = values.min(skipna=True)
    maximum = values.max(skipna=True)
    if pd.isna(minimum) or pd.isna(maximum) or abs(maximum - minimum) < 1e-9:
        return pd.Series(np.full(len(values), 0.5), index=values.index, dtype=float)
    return (values - minimum) / (maximum - minimum)


def _haversine_km(lat1: float, lon1: float, lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    radius = 6371.0
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2.astype(float))
    lon2 = np.radians(lon2.astype(float))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * radius * np.arcsin(np.sqrt(a))


def _source_boost(source: str) -> float:
    text = str(source).lower()
    if any(token in text for token in ["transit", "metro", "station", "mall"]):
        return 0.90
    if any(token in text for token in ["market", "university", "school"]):
        return 0.78
    if any(token in text for token in ["community", "park", "river"]):
        return 0.62
    return 0.50


def _risk_label(value: float) -> str:
    if value <= 0.33:
        return "low"
    if value <= 0.66:
        return "medium"
    return "high"


def _prediction_base(bundle: DataBundle) -> pd.DataFrame:
    if not bundle.predictions.empty:
        base = bundle.predictions.copy()
    elif not bundle.features.empty:
        keep = [
            col
            for col in [
                "grid_id",
                "point_id",
                "point_name",
                "lon",
                "lat",
                "source",
                "complaint_risk",
                "activity_proxy",
                "flow_proxy_score",
                "risk_level",
            ]
            if col in bundle.features.columns
        ]
        base = bundle.features[keep].copy()
        base["score"] = 0.55 * base.get("activity_proxy", 0.5) + 0.45 * (1 - base.get("complaint_risk", 0.5))
    else:
        base = bundle.candidates.copy()
        base["grid_id"] = base["point_id"]
        base["complaint_risk"] = 0.5
        base["activity_proxy"] = base["source"].map(_source_boost)
        base["flow_proxy_score"] = base["activity_proxy"]
        base["score"] = base["activity_proxy"]
        base["risk_level"] = "medium"

    if not bundle.candidates.empty:
        candidate_cols = [col for col in ["point_id", "point_name", "lon", "lat", "source"] if col in bundle.candidates.columns]
        base = base.drop(columns=[col for col in candidate_cols if col in base.columns and col != "point_id"], errors="ignore")
        base = base.merge(bundle.candidates[candidate_cols].drop_duplicates(subset=["point_id"]), on="point_id", how="left")

    for col in ["point_name", "source", "reason_1", "reason_2", "explanation_text", "risk_level"]:
        if col not in base.columns:
            base[col] = ""
    for col in ["lon", "lat", "score", "complaint_risk", "activity_proxy", "flow_proxy_score"]:
        if col not in base.columns:
            base[col] = np.nan

    base["score"] = pd.to_numeric(base["score"], errors="coerce").fillna(0.0)
    base["complaint_risk"] = pd.to_numeric(base["complaint_risk"], errors="coerce").fillna(0.5)
    base["activity_proxy"] = pd.to_numeric(base["activity_proxy"], errors="coerce").fillna(base["source"].map(_source_boost))
    base["flow_proxy_score"] = pd.to_numeric(base["flow_proxy_score"], errors="coerce").fillna(base["activity_proxy"])
    base["point_name"] = base["point_name"].fillna("未命名点位").astype(str)
    base["source"] = base["source"].fillna("unknown").astype(str)
    base["grid_id"] = base.get("grid_id", base["point_id"]).fillna(base["point_id"]).astype(str)
    return base.drop_duplicates(subset=["point_id"]).reset_index(drop=True)


def _complaint_stats_for_candidates(candidates: pd.DataFrame, complaints: pd.DataFrame) -> pd.DataFrame:
    if candidates.empty:
        return pd.DataFrame(columns=["point_id", "filtered_complaint_count", "filtered_top_category", "nearest_complaint_km"])
    if complaints.empty or not complaints.get("is_located", pd.Series(dtype=bool)).any():
        return pd.DataFrame(
            {
                "point_id": candidates["point_id"],
                "filtered_complaint_count": 0,
                "filtered_top_category": "",
                "nearest_complaint_km": np.nan,
            }
        )

    located = complaints[complaints["is_located"]].dropna(subset=["lat", "lon"]).copy()
    if located.empty:
        return pd.DataFrame(
            {
                "point_id": candidates["point_id"],
                "filtered_complaint_count": 0,
                "filtered_top_category": "",
                "nearest_complaint_km": np.nan,
            }
        )

    rows: list[dict[str, object]] = []
    complaint_lat = located["lat"].to_numpy(dtype=float)
    complaint_lon = located["lon"].to_numpy(dtype=float)
    for _, row in candidates.dropna(subset=["lat", "lon"]).iterrows():
        distances = _haversine_km(float(row["lat"]), float(row["lon"]), complaint_lat, complaint_lon)
        nearby = located.loc[distances <= 0.5]
        top_category = ""
        if not nearby.empty and "category" in nearby.columns:
            counts = nearby["category"].astype(str).value_counts()
            top_category = str(counts.index[0]) if not counts.empty else ""
        rows.append(
            {
                "point_id": row["point_id"],
                "filtered_complaint_count": int((distances <= 0.5).sum()),
                "filtered_top_category": top_category,
                "nearest_complaint_km": float(np.nanmin(distances)) if len(distances) else np.nan,
            }
        )

    stats = pd.DataFrame(rows)
    return candidates[["point_id"]].merge(stats, on="point_id", how="left").fillna(
        {"filtered_complaint_count": 0, "filtered_top_category": ""}
    )


def build_display_recommendations(bundle: DataBundle, filtered_complaints: pd.DataFrame) -> pd.DataFrame:
    base = _prediction_base(bundle)
    if base.empty:
        return base

    stats = _complaint_stats_for_candidates(base, filtered_complaints)
    out = base.merge(stats, on="point_id", how="left")
    out["filtered_complaint_count"] = pd.to_numeric(out["filtered_complaint_count"], errors="coerce").fillna(0)
    out["dynamic_complaint_risk"] = _normalize(out["filtered_complaint_count"])
    out["activity_proxy"] = pd.to_numeric(out["activity_proxy"], errors="coerce").fillna(out["source"].map(_source_boost))
    out["flow_proxy_score"] = pd.to_numeric(out["flow_proxy_score"], errors="coerce").fillna(out["activity_proxy"])
    out["base_score"] = pd.to_numeric(out["score"], errors="coerce").fillna(0.0)
    out["final_score"] = 0.60 * out["base_score"] + 0.25 * out["activity_proxy"] + 0.15 * (1 - out["dynamic_complaint_risk"])
    out["risk_level"] = out["dynamic_complaint_risk"].map(_risk_label)

    reason_1: list[str] = []
    reason_2: list[str] = []
    explanation: list[str] = []
    for _, row in out.iterrows():
        if row["activity_proxy"] >= 0.66:
            r1 = "活动代理分较高"
        elif row["dynamic_complaint_risk"] <= 0.33:
            r1 = "筛选后投诉压力较低"
        else:
            r1 = "基础排序稳定"

        if row["filtered_complaint_count"] == 0:
            r2 = "周边未发现筛选后投诉"
        elif row["dynamic_complaint_risk"] >= 0.66:
            r2 = "筛选后投诉仍较集中"
        elif row["filtered_top_category"]:
            r2 = f"周边高频问题为{row['filtered_top_category']}"
        else:
            r2 = "周边活跃度可支撑经营"

        reason_1.append(r1)
        reason_2.append(r2)
        explanation.append(f"{r1}，{r2}")

    out["reason_1"] = reason_1
    out["reason_2"] = reason_2
    out["explanation_text"] = explanation
    out = out.sort_values(["final_score", "dynamic_complaint_risk"], ascending=[False, True]).reset_index(drop=True)
    out["rank"] = np.arange(1, len(out) + 1)
    return out


def _filter_complaints(df: pd.DataFrame, start: pd.Timestamp | None, end: pd.Timestamp | None, categories: list[str]) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "created_at" in out.columns:
        out = out[out["created_at"].notna()].copy()
        if start is not None:
            out = out[out["created_at"] >= start]
        if end is not None:
            out = out[out["created_at"] <= end]
    if categories and "category" in out.columns:
        out = out[out["category"].isin(categories)]
    return out.reset_index(drop=True)


def _category_filter_options(df: pd.DataFrame) -> list[str]:
    if df.empty or "category" not in df.columns:
        return []
    preferred = ["噪声", "大气", "垃圾", "生态", "水", "其他"]
    observed = df["category"].fillna("").astype(str)
    return [label for label in preferred if observed.str.contains(label, regex=False).any()]


def _filter_complaints_by_theme(
    df: pd.DataFrame,
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
    selected_themes: list[str],
) -> pd.DataFrame:
    out = _filter_complaints(df, start, end, [])
    if not selected_themes or "category" not in out.columns:
        return out
    pattern = "|".join(selected_themes)
    return out[out["category"].fillna("").astype(str).str.contains(pattern, regex=True)].reset_index(drop=True)


def _theme_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    options = _category_filter_options(df)
    if df.empty or "category" not in df.columns or not options:
        return pd.DataFrame(columns=["theme", "count"])
    category_text = df["category"].fillna("").astype(str)
    rows = [{"theme": theme, "count": int(category_text.str.contains(theme, regex=False).sum())} for theme in options]
    return pd.DataFrame(rows)


def _build_homepage_metrics_clean(bundle: DataBundle, filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> pd.DataFrame:
    total = int(len(filtered_complaints))
    located = int(filtered_complaints.get("is_located", pd.Series(dtype=bool)).sum()) if total else 0
    located_ratio = f"{(located / total):.0%}" if total else "0%"
    candidate_count = int(len(bundle.candidates))
    high_suitability = int((pd.to_numeric(recommendations.get("final_score", pd.Series(dtype=float)), errors="coerce") >= 0.70).sum())
    high_risk = int((pd.to_numeric(recommendations.get("dynamic_complaint_risk", pd.Series(dtype=float)), errors="coerce") >= 0.66).sum())
    label_stats = label_summary(read_manual_labels())
    progress_denominator = max(candidate_count, 1)
    progress_value = f"{label_stats['labeled_rows']}/{candidate_count or 0}"
    progress_hint = f"覆盖率 {(label_stats['labeled_rows'] / progress_denominator):.0%}" if candidate_count else "暂无候选点"
    return pd.DataFrame(
        [
            {"label": "投诉总量", "value": f"{total:,}", "hint": "当前筛选范围内的真实投诉记录"},
            {"label": "定位覆盖率", "value": located_ratio, "hint": f"已定位 {located} 条投诉"},
            {"label": "候选点位", "value": f"{candidate_count:,}", "hint": "可参与推荐的候选点位"},
            {"label": "高适宜点位", "value": f"{high_suitability:,}", "hint": "综合得分不低于 0.70"},
            {"label": "高风险片区", "value": f"{high_risk:,}", "hint": "筛选后投诉风险仍偏高"},
            {"label": "标注进度", "value": progress_value, "hint": progress_hint},
        ]
    )


def _source_summary(bundle: DataBundle) -> pd.DataFrame:
    rows = []
    for key in ["complaints", "candidates", "features", "predictions"]:
        path = bundle.sources.get(key, "missing")
        status = "演示数据" if path == "demo" else ("缺失" if path == "missing" else "已加载")
        rows.append({"数据表": key, "状态": status, "路径": path})
    return pd.DataFrame(rows)


def _evidence_items() -> list[tuple[str, Path]]:
    items = [
        ("上海开放平台 12345 工单办理详情页", EVIDENCE_ROOT / "shanghai_open_12345_detail.png"),
        ("上海开放平台 杨浦区生态环境点位数据详情页", EVIDENCE_ROOT / "yangpu_environment_points_detail.png"),
    ]
    return [(label, path) for label, path in items if path.exists()]


def _generated_asset_items() -> list[tuple[str, Path]]:
    items: list[tuple[str, Path]] = []
    for root, prefix in [(FIGURE_ROOT, "论文配图"), (SCREENSHOT_ROOT, "答辩截图")]:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.png")):
            items.append((f"{prefix}: {path.name}", path))
    return items


def _prepare_label_editor_frame(bundle: DataBundle, recommendations: pd.DataFrame) -> pd.DataFrame:
    existing = read_manual_labels()
    template = build_label_template(bundle.candidates, bundle.features, bundle.predictions, existing)
    if "labeled_at" in template.columns:
        template["labeled_at"] = pd.to_datetime(template["labeled_at"], errors="coerce")
    if recommendations.empty:
        return template.sort_values(["score", "point_name"], ascending=[False, True]).reset_index(drop=True)

    ranking = recommendations[["point_id", "final_score"]].drop_duplicates(subset=["point_id"]).copy()
    template = template.merge(ranking, on="point_id", how="left")
    template = template.sort_values(["final_score", "score", "point_name"], ascending=[False, False, True]).reset_index(drop=True)
    return template.drop(columns=["final_score"])


def _persist_labels_and_retrain(bundle: DataBundle, edited_labels: pd.DataFrame) -> dict[str, object]:
    saved_path = save_manual_labels(edited_labels, manual_labels_path())
    labels = read_manual_labels(saved_path)
    result: dict[str, object] = {"saved_path": str(saved_path), "label_summary": label_summary(labels)}

    if bundle.features.empty:
        result["retrained"] = False
        result["reason"] = "features_missing"
        return result

    merged_features = merge_manual_labels(bundle.features, labels)
    write_csv(merged_features, PROCESSED_ROOT / "features.csv")

    artifact_root = artifacts_dir()
    model_payload, metrics = train_model(merged_features)
    model_path = artifact_root / "ranking_model.joblib"
    coef_path = artifact_root / "feature_coefficients.csv"

    if model_payload:
        joblib.dump(model_payload, model_path)
        coefficients = model_payload.get("coefficients", {})
        if coefficients:
            coef_df = (
                pd.DataFrame({"feature": list(coefficients.keys()), "coefficient": list(coefficients.values())})
                .sort_values("coefficient", ascending=False)
                .reset_index(drop=True)
            )
            write_csv(coef_df, coef_path)
    else:
        if model_path.exists():
            model_path.unlink()
        if coef_path.exists():
            coef_path.unlink()

    predictions, meta = predict(merged_features, artifact_root)
    write_csv(predictions, PROCESSED_ROOT / "predictions.csv")
    write_json(meta, PROCESSED_ROOT / "prediction_report.json")
    write_json(metrics, artifact_root / "metrics.json")

    result["retrained"] = True
    result["metrics"] = metrics
    result["prediction_meta"] = meta
    return result


def _build_map(complaints: pd.DataFrame, recommendations: pd.DataFrame) -> folium.Map:
    center_lat = 31.285
    center_lon = 121.52
    if not recommendations.empty and recommendations["lat"].notna().any():
        center_lat = float(recommendations["lat"].dropna().mean())
        center_lon = float(recommendations["lon"].dropna().mean())
    elif not complaints.empty and complaints["lat"].notna().any():
        center_lat = float(complaints["lat"].dropna().mean())
        center_lon = float(complaints["lon"].dropna().mean())

    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="CartoDB positron")

    located = complaints[complaints.get("is_located", False)].dropna(subset=["lat", "lon"])
    if not located.empty:
        HeatMap(located[["lat", "lon"]].values.tolist(), radius=22, blur=18, min_opacity=0.35).add_to(fmap)

    top_points = recommendations.head(10).dropna(subset=["lat", "lon"])
    for _, row in top_points.iterrows():
        color = "#0f766e" if int(row["rank"]) <= 3 else "#f97316"
        tooltip = (
            f"#{int(row['rank'])} {row['point_name']}<br>"
            f"得分: {float(row['final_score']):.3f}<br>"
            f"风险: {row['risk_level']}<br>"
            f"周边投诉: {int(row['filtered_complaint_count'])}"
        )
        folium.CircleMarker(
            location=[float(row["lat"]), float(row["lon"])],
            radius=8 if int(row["rank"]) <= 3 else 6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=tooltip,
        ).add_to(fmap)

    return fmap


def _download_csv_button(label: str, df: pd.DataFrame, filename: str, key: str) -> None:
    st.download_button(
        label,
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
        key=key,
    )


def _read_model_diagnostics() -> tuple[dict[str, object], pd.DataFrame]:
    artifact_root = artifacts_dir()
    metrics_path = artifact_root / "metrics.json"
    coef_path = artifact_root / "feature_coefficients.csv"
    metrics: dict[str, object] = {}
    coefficients = pd.DataFrame()
    if metrics_path.exists():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    if coef_path.exists():
        coefficients = pd.read_csv(coef_path)
    return metrics, coefficients


def _latest_update_text(bundle: DataBundle) -> str:
    if not bundle.complaints.empty and "created_at" in bundle.complaints.columns:
        latest = pd.to_datetime(bundle.complaints["created_at"], errors="coerce").dropna()
        if not latest.empty:
            return latest.max().strftime("%Y-%m-%d %H:%M")
    return pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")


def _build_homepage_metrics(bundle: DataBundle, filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> pd.DataFrame:
    total = int(len(filtered_complaints))
    located = int(filtered_complaints.get("is_located", pd.Series(dtype=bool)).sum()) if total else 0
    located_ratio = f"{(located / total):.0%}" if total else "0%"
    candidate_count = int(len(bundle.candidates))
    high_suitability = int((pd.to_numeric(recommendations.get("final_score", pd.Series(dtype=float)), errors="coerce") >= 0.70).sum())
    high_risk = int((pd.to_numeric(recommendations.get("dynamic_complaint_risk", pd.Series(dtype=float)), errors="coerce") >= 0.66).sum())
    label_stats = label_summary(read_manual_labels())
    progress_denominator = max(candidate_count, 1)
    progress_value = f"{label_stats['labeled_rows']}/{candidate_count or 0}"
    progress_hint = f"覆盖率 {(label_stats['labeled_rows'] / progress_denominator):.0%}" if candidate_count else "暂无候选点"
    return pd.DataFrame(
        [
            {"label": "投诉总量", "value": f"{total:,}", "hint": "当前筛选范围内的投诉记录"},
            {"label": "定位覆盖率", "value": located_ratio, "hint": f"已定位 {located} 条投诉"},
            {"label": "候选点位", "value": f"{candidate_count:,}", "hint": "可参与推荐的候选点位"},
            {"label": "高适宜点位", "value": f"{high_suitability:,}", "hint": "综合得分不低于 0.70"},
            {"label": "高风险片区", "value": f"{high_risk:,}", "hint": "筛选后投诉风险仍偏高"},
            {"label": "标注进度", "value": progress_value, "hint": progress_hint},
        ]
    )


def _module_entries() -> list[dict[str, str]]:
    return [
        {"title": "点位推荐", "summary": "面向治理管理者查看候选点排序、得分解释和空间分布。", "target": "推荐分析"},
        {"title": "投诉监测", "summary": "查看投诉主题、热点态势和巡查优先级。", "target": "投诉监测"},
        {"title": "人工标注", "summary": "补充适宜性标签，为后续真实工单接入和模型重训预留接口。", "target": "人工标注"},
        {"title": "模型诊断", "summary": "查看当前模型来源、样本量和系数。", "target": "模型诊断"},
        {"title": "证据中心", "summary": "浏览开放平台截图、论文配图和答辩素材。", "target": "证据导出"},
        {"title": "结果导出", "summary": "按当前筛选导出推荐、投诉和特征结果。", "target": "证据导出"},
    ]


def _render_shell_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #07111b;
            --bg-soft: #0b1623;
            --panel: rgba(13, 23, 36, 0.92);
            --panel-strong: #101c2b;
            --ink: #e9f0f8;
            --muted: #9bb0c6;
            --line: rgba(120, 144, 168, 0.22);
            --teal: #22c7b8;
            --teal-soft: rgba(34, 199, 184, 0.16);
            --warn: #f59e0b;
            --shadow: 0 18px 50px rgba(0, 0, 0, 0.32);
        }
        .stApp {
            background:
              radial-gradient(circle at 0% 0%, rgba(34,199,184,0.16), transparent 26%),
              radial-gradient(circle at 100% 0%, rgba(245,158,11,0.12), transparent 20%),
              linear-gradient(180deg, #08111c 0%, var(--bg) 100%);
            color: var(--ink);
        }
        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
        }
        .block-container {
            padding-top: 0.6rem;
            padding-bottom: 3rem;
            max-width: 1440px;
        }
        h1, h2, h3, h4, h5, h6, p, label, span, div, .stMarkdown, .stCaption {
            color: var(--ink);
        }
        .platform-hero {
            background: linear-gradient(135deg, #0e1b2d 0%, #12324b 52%, #0f766e 100%);
            color: white;
            border-radius: 28px;
            padding: 1.5rem 1.6rem;
            margin-bottom: 1rem;
            box-shadow: 0 28px 80px rgba(0, 0, 0, 0.36);
            border: 1px solid rgba(110, 140, 170, 0.18);
        }
        .platform-hero .eyebrow {
            display: inline-block;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-size: 0.72rem;
            opacity: 0.82;
            margin-bottom: 0.55rem;
        }
        .platform-hero h1 {
            margin: 0;
            font-size: 2.25rem;
            line-height: 1.15;
        }
        .platform-hero p {
            margin: 0.55rem 0 0;
            max-width: 62rem;
            color: rgba(255,255,255,0.88);
            line-height: 1.6;
        }
        .status-strip {
            display: grid;
            grid-template-columns: 1.2fr 1fr 1fr;
            gap: 0.8rem;
            margin-top: 1rem;
        }
        .status-item {
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 18px;
            padding: 0.9rem 1rem;
            backdrop-filter: blur(10px);
        }
        .status-item .label {
            font-size: 0.76rem;
            opacity: 0.75;
            margin-bottom: 0.22rem;
        }
        .status-item .value {
            font-size: 1rem;
            font-weight: 700;
        }
        .section-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow);
        }
        .section-title {
            font-size: 1rem;
            font-weight: 700;
            color: var(--ink);
            margin-bottom: 0.55rem;
        }
        .summary-list {
            display: grid;
            gap: 0.75rem;
        }
        .summary-item {
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.85rem 0.9rem;
            background: linear-gradient(180deg, rgba(20, 32, 49, 0.98) 0%, rgba(12, 22, 35, 0.98) 100%);
        }
        .summary-item .title {
            font-size: 0.82rem;
            color: var(--muted);
            margin-bottom: 0.24rem;
        }
        .summary-item .body {
            font-size: 0.98rem;
            color: var(--ink);
            font-weight: 600;
            line-height: 1.45;
        }
        .rank-card {
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.95rem;
            margin-bottom: 0.8rem;
            background: linear-gradient(180deg, rgba(18, 30, 46, 0.98) 0%, rgba(11, 20, 31, 0.98) 100%);
        }
        .rank-card .rank-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }
        .rank-card .rank-no {
            color: var(--teal);
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.04em;
        }
        .rank-card .risk-tag {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            background: var(--teal-soft);
            color: var(--teal);
        }
        .rank-card .name {
            font-size: 1.02rem;
            font-weight: 700;
            color: var(--ink);
            margin-bottom: 0.3rem;
        }
        .rank-card .meta {
            color: var(--muted);
            font-size: 0.82rem;
            margin-bottom: 0.45rem;
        }
        .rank-card .reason {
            color: var(--ink);
            line-height: 1.55;
            font-size: 0.9rem;
        }
        .module-card {
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 1rem;
            min-height: 172px;
            background: linear-gradient(180deg, #ffffff 0%, #f8fbfd 100%);
        }
        .module-card h4 {
            margin: 0 0 0.4rem;
            color: var(--ink);
            font-size: 1rem;
        }
        .module-card p {
            margin: 0;
            color: var(--muted);
            line-height: 1.55;
            font-size: 0.88rem;
        }
        .module-caption {
            font-size: 0.76rem;
            color: var(--muted);
            margin-top: 0.6rem;
        }
        .top-nav-block {
            margin-bottom: 0.9rem;
        }
        [data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(16, 28, 43, 0.96) 0%, rgba(10, 18, 29, 0.96) 100%);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.8rem 0.9rem;
            box-shadow: var(--shadow);
        }
        [data-testid="stMetricLabel"] label,
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {
            color: var(--ink) !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid var(--line) !important;
            background: linear-gradient(180deg, rgba(15, 25, 39, 0.96) 0%, rgba(10, 18, 29, 0.96) 100%);
            box-shadow: var(--shadow);
        }
        div[data-testid="stAlert"] {
            background: rgba(14, 26, 41, 0.92);
            color: var(--ink);
            border: 1px solid var(--line);
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }
        div[data-testid="stDataFrame"] * {
            color: var(--ink) !important;
        }
        div[data-testid="stDataEditor"] {
            border: 1px solid var(--line);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: var(--shadow);
        }
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-testid="stDateInput"] > div > div,
        [data-testid="stNumberInput"] > div > div,
        [data-testid="stTextInput"] > div > div {
            background: rgba(12, 22, 35, 0.94) !important;
            border: 1px solid var(--line) !important;
            color: var(--ink) !important;
        }
        input, textarea {
            color: var(--ink) !important;
        }
        [data-testid="stMultiSelect"] span,
        [data-testid="stDateInput"] input {
            color: var(--ink) !important;
        }
        [data-testid="stSlider"] [role="slider"] {
            background: var(--teal) !important;
        }
        [data-testid="stSliderTickBarMin"] {
            background-color: var(--teal) !important;
        }
        div[role="radiogroup"] {
            display: flex;
            gap: 0.8rem;
            margin: 0.25rem 0 1rem;
        }
        div[role="radiogroup"] label {
            background: rgba(15, 26, 41, 0.96);
            border: 1px solid var(--line);
            border-radius: 999px;
            padding: 0.55rem 1rem;
            color: var(--ink) !important;
        }
        button[kind="secondary"],
        button[kind="primary"] {
            border-radius: 999px !important;
        }
        iframe {
            border-radius: 22px !important;
            overflow: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_brand_header(bundle: DataBundle) -> None:
    data_status = "本地真实数据已接入" if not bundle.demo_mode else "当前使用演示数据"
    latest_update = _latest_update_text(bundle)
    source_status = "正式运行模式" if not bundle.demo_mode else "演示模式"
    st.markdown(
        f"""
        <div class="platform-hero">
          <div class="eyebrow">Yangpu Operations Dashboard</div>
          <h1>杨浦区流动经营点位决策平台</h1>
          <p>面向运营方的街区级点位推荐、投诉监测与解释性分析首页。系统基于投诉替代集、候选点位、天气与节假日数据，为点位投放和风险控制提供统一入口。</p>
          <div class="status-strip">
            <div class="status-item"><div class="label">系统状态</div><div class="value">{source_status}</div></div>
            <div class="status-item"><div class="label">数据状态</div><div class="value">{data_status}</div></div>
            <div class="status-item"><div class="label">最近更新时间</div><div class="value">{latest_update}</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_homepage_metric_band(metrics_frame: pd.DataFrame) -> None:
    metric_cols = st.columns(len(metrics_frame))
    for col, (_, row) in zip(metric_cols, metrics_frame.iterrows(), strict=False):
        with col:
            st.metric(str(row["label"]), str(row["value"]), str(row["hint"]))


def _build_summary_items(filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> list[tuple[str, str]]:
    if filtered_complaints.empty:
        return [
            ("本周运营摘要", "当前筛选范围内暂无投诉记录，建议优先检查筛选条件或加载完整数据。"),
            ("风险变化", "暂无有效风险变化可比对。"),
            ("重点问题", "暂无高频投诉类型。"),
        ]
    category_counts = filtered_complaints["category"].astype(str).value_counts()
    top_category = str(category_counts.index[0]) if not category_counts.empty else "未分类"
    top_point = str(recommendations.iloc[0]["point_name"]) if not recommendations.empty else "暂无"
    high_risk = int((pd.to_numeric(recommendations.get("dynamic_complaint_risk", pd.Series(dtype=float)), errors="coerce") >= 0.66).sum())
    return [
        ("本周运营摘要", f"当前筛选范围共 {len(filtered_complaints)} 条投诉，建议优先关注推荐点位与高风险片区的联动变化。"),
        ("风险变化", f"当前识别出 {high_risk} 个高风险片区，建议先处理与推荐点位邻近的热点区域。"),
        ("重点问题", f"高频投诉类型为“{top_category}”，当前综合推荐第一位是“{top_point}”。"),
    ]


def _render_summary_panel(filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> None:
    items = _build_summary_items(filtered_complaints, recommendations)
    blocks = []
    for title, body in items:
        blocks.append(
            f"""
            <div class="summary-item">
              <div class="title">{title}</div>
              <div class="body">{body}</div>
            </div>
            """
        )
    st.html(
        f"""
        <div class="section-card">
          <div class="section-title">运营摘要</div>
          <div class="summary-list">
            {''.join(blocks)}
          </div>
        </div>
        """
    )


def _render_top_recommendation_cards(recommendations: pd.DataFrame) -> None:
    if recommendations.empty:
        st.info("当前筛选条件下没有可展示的推荐点位。")
        return
    cards: list[str] = []
    for _, row in recommendations.head(3).iterrows():
        cards.append(
            f"""
            <div class="rank-card">
              <div class="rank-head">
                <div class="rank-no">TOP {int(row['rank'])}</div>
                <div class="risk-tag">{str(row['risk_level']).upper()}</div>
              </div>
              <div class="name">{row['point_name']}</div>
              <div class="meta">类型：{row['source']} | 综合得分：{float(row['final_score']):.3f}</div>
              <div class="reason">{row['reason_1']}；{row['reason_2']}</div>
            </div>
            """
        )
    st.html(
        f"""
        <div class="section-card">
          <div class="section-title">今日建议点位</div>
          {''.join(cards)}
        </div>
        """
    )


def _render_dashboard_insights(filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> None:
    insight_col, table_col = st.columns([1.05, 1])
    with insight_col:
        st.markdown("### 投诉观察")
        if not filtered_complaints.empty and "category" in filtered_complaints.columns:
            category_counts = (
                filtered_complaints["category"].astype(str).value_counts().rename_axis("category").reset_index(name="count").head(8)
            )
            st.bar_chart(category_counts.set_index("category"))
        else:
            st.info("当前筛选条件下没有可展示的投诉分类分布。")

    with table_col:
        st.markdown("### 推荐总览")
        if recommendations.empty:
            st.info("当前筛选条件下没有可展示的推荐结果。")
        else:
            preview = recommendations.head(6).copy()
            st.dataframe(
                preview[
                    ["rank", "point_name", "source", "final_score", "risk_level", "filtered_complaint_count"]
                ].rename(
                    columns={
                        "rank": "排名",
                        "point_name": "点位名称",
                        "source": "类型",
                        "final_score": "综合得分",
                        "risk_level": "风险等级",
                        "filtered_complaint_count": "周边投诉数",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )


def _render_dashboard_footer(bundle: DataBundle, filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> None:
    st.markdown("### 更多工具")
    with st.expander("展开人工标注、模型诊断与证据导出", expanded=False):
        tabs = st.tabs(["人工标注", "模型诊断", "证据导出"])
        with tabs[0]:
            _render_labeling_view(bundle, recommendations)
        with tabs[1]:
            _render_model_view()
        with tabs[2]:
            _render_evidence_and_exports(bundle, filtered_complaints, recommendations)


def _render_module_cards() -> None:
    st.markdown("### 业务模块")
    entries = _module_entries()
    for offset in range(0, len(entries), 3):
        cols = st.columns(3)
        for col, entry in zip(cols, entries[offset : offset + 3], strict=False):
            with col:
                st.markdown(
                    f"""
                    <div class="module-card">
                      <h4>{entry['title']}</h4>
                      <p>{entry['summary']}</p>
                      <div class="module-caption">进入：{entry['target']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"进入{entry['title']}", key=f"module-{entry['title']}", use_container_width=True):
                    st.session_state["active_nav"] = entry["target"]
                    st.rerun()


def _render_recommendation_analysis(recommendations: pd.DataFrame) -> None:
    st.markdown("### 推荐分析")
    detail_col, top_col = st.columns([1.05, 1])
    with detail_col:
        st.markdown("#### 候选点得分拆解")
        if not recommendations.empty:
            selected_name = st.selectbox("选择点位", recommendations["point_name"].tolist(), key="recommendation_select")
            selected_row = recommendations[recommendations["point_name"] == selected_name].iloc[0]
            component_columns = [
                ("activity_component", "活动活跃"),
                ("flow_component", "流量代理"),
                ("temporal_component", "时段机会"),
                ("stability_component", "天气稳定"),
                ("low_complaint_component", "低投诉压力"),
                ("street_friendly_component", "道路友好"),
            ]
            component_rows = []
            for col, label in component_columns:
                value = pd.to_numeric(selected_row.get(col, 0.0), errors="coerce")
                component_rows.append({"指标": label, "值": 0.0 if pd.isna(value) else float(value)})
            st.bar_chart(pd.DataFrame(component_rows).set_index("指标"))
            st.caption(str(selected_row.get("explanation_text", "")))
        else:
            st.info("当前没有可分析的推荐点位。")
    with top_col:
        st.markdown("#### Top3 推荐")
        if recommendations.empty:
            st.warning("暂无推荐结果。")
        else:
            top3 = recommendations.head(3).copy()
            st.dataframe(
                top3[
                    ["rank", "point_name", "source", "final_score", "risk_level", "filtered_complaint_count", "reason_1", "reason_2"]
                ].rename(
                    columns={
                        "rank": "排名",
                        "point_name": "点位名称",
                        "source": "类型",
                        "final_score": "最终得分",
                        "risk_level": "风险等级",
                        "filtered_complaint_count": "周边投诉数",
                        "reason_1": "主理由",
                        "reason_2": "补充理由",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
            _download_csv_button("导出当前推荐结果", recommendations, "predictions_export.csv", key="legacy-evidence-predictions")


def _render_monitoring_view(bundle: DataBundle, filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> None:
    st.markdown("### 投诉监测")
    monitor_left, monitor_right = st.columns([1.45, 1])
    with monitor_left:
        st.markdown("#### 热点与推荐态势地图")
        st_folium(_build_map(filtered_complaints, recommendations), width=None, height=560, returned_objects=[])
    with monitor_right:
        st.markdown("#### 投诉类别分布")
        if not filtered_complaints.empty and "category" in filtered_complaints.columns:
            category_counts = filtered_complaints["category"].astype(str).value_counts().rename_axis("category").reset_index(name="count")
            st.bar_chart(category_counts.set_index("category"))
        else:
            st.info("当前筛选条件下没有可展示的投诉类别分布。")

        quality_rows = pd.DataFrame(
            [
                {"指标": "过滤后投诉数", "值": int(len(filtered_complaints))},
                {"指标": "过滤后已定位投诉", "值": int(filtered_complaints.get("is_located", pd.Series(dtype=bool)).sum())},
                {"指标": "推荐结果数", "值": int(len(recommendations))},
                {"指标": "候选点类型数", "值": int(bundle.candidates.get("source", pd.Series(dtype=str)).nunique()) if not bundle.candidates.empty else 0},
            ]
        )
        st.markdown("#### 数据质量摘要")
        st.dataframe(quality_rows, use_container_width=True, hide_index=True)


def _render_labeling_view(bundle: DataBundle, recommendations: pd.DataFrame) -> None:
    st.markdown("### 人工标注")
    label_file = manual_labels_path()
    existing_labels = read_manual_labels(label_file)
    label_stats = label_summary(existing_labels)
    st.caption(
        f"当前已保存标注 {label_stats['labeled_rows']} 条，正样本 {label_stats['positive_labels']} 条，负样本 {label_stats['negative_labels']} 条。"
    )
    label_editor = _prepare_label_editor_frame(bundle, recommendations)
    label_editor["label"] = pd.to_numeric(label_editor["label"], errors="coerce")
    if "labeled_at" in label_editor.columns:
        label_editor["labeled_at"] = (
            pd.to_datetime(label_editor["labeled_at"], errors="coerce")
            .dt.strftime("%Y-%m-%d %H:%M:%S")
            .fillna("")
        )
    edited_labels = st.data_editor(
        label_editor,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "point_id": st.column_config.TextColumn("点位ID", disabled=True),
            "point_name": st.column_config.TextColumn("点位名称", disabled=True),
            "source": st.column_config.TextColumn("类型", disabled=True),
            "score": st.column_config.NumberColumn("当前得分", format="%.3f", disabled=True),
            "complaint_risk": st.column_config.NumberColumn("投诉风险", format="%.3f", disabled=True),
            "activity_proxy": st.column_config.NumberColumn("活动代理", format="%.3f", disabled=True),
            "label": st.column_config.SelectboxColumn("人工标签", options=[None, 1, 0], help="1 表示适宜推荐，0 表示不适宜推荐"),
            "label_source": st.column_config.TextColumn("标签来源"),
            "label_notes": st.column_config.TextColumn("标注备注"),
            "labeled_by": st.column_config.TextColumn("标注人"),
            "labeled_at": st.column_config.TextColumn("标注时间"),
        },
    )

    action_cols = st.columns([1, 1, 1.2])
    with action_cols[0]:
        if st.button("保存人工标注", use_container_width=True):
            save_manual_labels(edited_labels, label_file)
            st.session_state["label_action_result"] = {
                "mode": "saved",
                "path": str(label_file),
                "summary": label_summary(read_manual_labels(label_file)),
            }
    with action_cols[1]:
        if st.button("保存并重训模型", type="primary", use_container_width=True):
            st.session_state["label_action_result"] = _persist_labels_and_retrain(bundle, edited_labels)
    with action_cols[2]:
        _download_csv_button("下载标注模板 CSV", label_editor, "manual_labels_template.csv", key="legacy-label-template")

    label_action_result = st.session_state.get("label_action_result")
    if label_action_result:
        if label_action_result.get("mode") == "saved":
            summary = label_action_result["summary"]
            st.success(f"已保存人工标注到 {label_action_result['path']}。当前有效标注 {summary['labeled_rows']} 条。")
        elif label_action_result.get("retrained"):
            metrics = label_action_result.get("metrics", {})
            st.success(f"已保存标注并完成重训。模型来源：{metrics.get('model_source')}，有效标注 {metrics.get('labeled_rows')} 条。")
        else:
            st.info("标注已保存，但当前还没有足够的特征数据可用于重训。")


def _render_model_view() -> None:
    st.markdown("### 模型诊断")
    metrics, coefficients = _read_model_diagnostics()
    if not metrics:
        st.info("当前还没有模型诊断结果。保存人工标注并重训后，这里会显示样本量和系数。")
        return
    diag_cols = st.columns(4)
    diag_cols[0].metric("模型来源", str(metrics.get("model_source", "-")))
    diag_cols[1].metric("标注样本数", str(metrics.get("labeled_rows", 0)))
    diag_cols[2].metric("准确率", "-" if metrics.get("accuracy") is None else f"{float(metrics['accuracy']):.3f}")
    diag_cols[3].metric("F1", "-" if metrics.get("f1") is None else f"{float(metrics['f1']):.3f}")
    if not coefficients.empty:
        st.markdown("#### 特征系数")
        st.dataframe(coefficients.head(12), use_container_width=True, hide_index=True)


def _render_evidence_and_exports(bundle: DataBundle, filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> None:
    st.markdown("### 证据导出")
    evidence_items = _evidence_items()
    if evidence_items:
        st.markdown("#### 开放平台证据")
        cols = st.columns(len(evidence_items))
        for col, (label, path) in zip(cols, evidence_items, strict=False):
            with col:
                st.image(str(path), caption=label, use_container_width=True)

    generated_assets = _generated_asset_items()
    if generated_assets:
        st.markdown("#### 论文配图与答辩截图")
        preview_cols = st.columns(2)
        for index, (label, path) in enumerate(generated_assets[:6]):
            with preview_cols[index % 2]:
                st.image(str(path), caption=label, use_container_width=True)

    st.markdown("#### 结果导出")
    export_cols = st.columns(3)
    with export_cols[0]:
        _download_csv_button("下载推荐结果 CSV", recommendations, "predictions_export.csv", key="legacy-evidence-predictions")
    with export_cols[1]:
        _download_csv_button("下载筛选后投诉 CSV", filtered_complaints, "complaints_filtered.csv", key="legacy-evidence-complaints")
    with export_cols[2]:
        _download_csv_button("下载特征表预览 CSV", bundle.features.head(200), "features_preview.csv", key="legacy-evidence-features")

    with st.expander("查看数据状态与原始数据预览"):
        st.dataframe(_source_summary(bundle), use_container_width=True, hide_index=True)
        tabs = st.tabs(["投诉", "候选点", "特征", "预测"])
        with tabs[0]:
            st.dataframe(bundle.complaints.head(20), use_container_width=True)
        with tabs[1]:
            st.dataframe(bundle.candidates.head(20), use_container_width=True)
        with tabs[2]:
            st.dataframe(bundle.features.head(20), use_container_width=True)
        with tabs[3]:
            st.dataframe(bundle.predictions.head(20), use_container_width=True)


def _render_brand_header_clean(bundle: DataBundle) -> None:
    data_status = "\u672c\u5730\u771f\u5b9e\u6570\u636e\u5df2\u63a5\u5165" if not bundle.demo_mode else "\u5f53\u524d\u4f7f\u7528\u6f14\u793a\u6570\u636e"
    source_status = "\u6b63\u5f0f\u8fd0\u884c\u6a21\u5f0f" if not bundle.demo_mode else "\u6f14\u793a\u6a21\u5f0f"
    latest_update = _latest_update_text(bundle)
    st.markdown(
        f"""
        <div class="platform-hero">
          <div class="eyebrow">Yangpu Governance Dashboard</div>
          <h1>杨浦区地摊经济监测与点位决策支持平台</h1>
          <p>面向街区治理管理者和一线巡查人员，用于查看投诉热点、筛选候选点位、解释推荐依据，并导出当前决策证据。</p>
          <div class="status-strip">
            <div class="status-item"><div class="label">\u7cfb\u7edf\u72b6\u6001</div><div class="value">{source_status}</div></div>
            <div class="status-item"><div class="label">\u6570\u636e\u72b6\u6001</div><div class="value">{data_status}</div></div>
            <div class="status-item"><div class="label">\u6700\u8fd1\u66f4\u65b0\u65f6\u95f4</div><div class="value">{latest_update}</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _build_summary_items_clean(filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> list[tuple[str, str]]:
    if filtered_complaints.empty:
        return [
            ("本周治理摘要", "当前筛选范围内暂无投诉记录。"),
            ("\u98ce\u9669\u53d8\u5316", "\u6682\u65e0\u53ef\u6bd4\u5bf9\u7684\u98ce\u9669\u53d8\u5316\u3002"),
            ("\u91cd\u70b9\u95ee\u9898", "\u6682\u65e0\u9ad8\u9891\u6295\u8bc9\u7c7b\u578b\u3002"),
        ]
    theme_counts = _theme_breakdown(filtered_complaints)
    top_category = str(theme_counts.iloc[0]["theme"]) if not theme_counts.empty else "\u672a\u5206\u7c7b"
    top_point = str(recommendations.iloc[0]["point_name"]) if not recommendations.empty else "\u6682\u65e0"
    high_risk = int((pd.to_numeric(recommendations.get("dynamic_complaint_risk", pd.Series(dtype=float)), errors="coerce") >= 0.66).sum())
    return [
        ("本周治理摘要", f"当前筛选范围共 {len(filtered_complaints)} 条投诉，建议优先关注推荐点位与周边风险区域。"),
        ("\u98ce\u9669\u53d8\u5316", f"\u5f53\u524d\u8bc6\u522b\u51fa {high_risk} \u4e2a\u9ad8\u98ce\u9669\u7247\u533a\uff0c\u5efa\u8bae\u4f18\u5148\u5904\u7406\u4e0e\u63a8\u8350\u70b9\u4f4d\u90bb\u8fd1\u7684\u70ed\u70b9\u533a\u57df\u3002"),
        ("\u91cd\u70b9\u95ee\u9898", f"\u9ad8\u9891\u6295\u8bc9\u7c7b\u578b\u4e3a\u201c{top_category}\u201d\uff0c\u5f53\u524d\u7efc\u5408\u63a8\u8350\u7b2c\u4e00\u4f4d\u662f\u201c{top_point}\u201d\u3002"),
    ]


def _render_summary_panel_clean(filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> None:
    st.markdown("### 治理摘要")
    for title, body in _build_summary_items_clean(filtered_complaints, recommendations):
        with st.container(border=True):
            st.caption(title)
            st.write(body)


def _render_top_recommendation_cards_clean(recommendations: pd.DataFrame) -> None:
    st.markdown("### \u4eca\u65e5\u5efa\u8bae\u70b9\u4f4d")
    if recommendations.empty:
        st.info("\u5f53\u524d\u7b5b\u9009\u6761\u4ef6\u4e0b\u6ca1\u6709\u53ef\u5c55\u793a\u7684\u63a8\u8350\u7ed3\u679c\u3002")
        return
    for _, row in recommendations.head(3).iterrows():
        with st.container(border=True):
            title_col, risk_col = st.columns([1, 0.5])
            title_col.markdown(f"**TOP {int(row['rank'])} | {row['point_name']}**")
            risk_col.caption(f"\u98ce\u9669\u7b49\u7ea7: {str(row['risk_level']).upper()}")
            st.caption(f"\u7c7b\u578b: {row['source']} | \u7efc\u5408\u5f97\u5206: {float(row['final_score']):.3f}")
            st.write(f"{row['reason_1']}\uff1b{row['reason_2']}")


def _render_filter_panel_clean(bundle: DataBundle) -> tuple[pd.Timestamp | None, pd.Timestamp | None, list[str], list[str], int, float]:
    st.markdown("### 驾驶舱筛选")
    complaint_dates = bundle.complaints.get("created_at", pd.Series(dtype="datetime64[ns]")).dropna()
    theme_options = _category_filter_options(bundle.complaints)
    sources = sorted(bundle.candidates.get("source", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())

    with st.container(border=True):
        st.caption("筛选条件来自当前已接入的投诉数据、候选点位数据和地理清洗结果，服务于管理者巡查与点位研判。")
        summary_cols = st.columns(4)
        summary_cols[0].metric("数据时间范围", "可筛选", "-" if complaint_dates.empty else f"{complaint_dates.min().date()} 至 {complaint_dates.max().date()}")
        summary_cols[1].metric("投诉主题数", str(len(theme_options)), "已按真实投诉文本聚合")
        summary_cols[2].metric("候选点类型", str(len(sources)), "来自杨浦区真实候选点")
        summary_cols[3].metric("定位成功率", f"{bundle.complaints.get('is_located', pd.Series(dtype=bool)).mean():.0%}" if not bundle.complaints.empty else "0%", "用于地图展示")

        top_filter_cols = st.columns([1.2, 1.15, 1.05])
        bottom_filter_cols = st.columns([0.85, 0.85, 1.3])

        if complaint_dates.empty:
            start = end = None
            with top_filter_cols[0]:
                st.info("暂无可用时间范围")
        else:
            with top_filter_cols[0]:
                selected_range = st.date_input(
                    "投诉时间范围",
                    value=(complaint_dates.min().date(), complaint_dates.max().date()),
                    key="dashboard_date_range",
                )
            if isinstance(selected_range, tuple) and len(selected_range) == 2:
                start = pd.Timestamp(selected_range[0])
                end = pd.Timestamp(selected_range[1]) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            else:
                start = end = None

        with top_filter_cols[1]:
            selected_themes = st.multiselect(
                "投诉主题",
                theme_options,
                default=theme_options,
                key="dashboard_theme_categories",
                help="基于真实投诉类别提炼为 6 个可操作主题，组合类目会自动归并到这些主题下。",
            )

        with top_filter_cols[2]:
            selected_sources = st.multiselect(
                "候选点类型",
                sources,
                default=sources,
                key="dashboard_sources",
            )

        with bottom_filter_cols[0]:
            top_n = st.slider("展示数量", min_value=3, max_value=12, value=6, key="dashboard_top_n")

        with bottom_filter_cols[1]:
            score_floor = st.slider("最低得分", min_value=0.0, max_value=1.0, value=0.0, step=0.05, key="dashboard_score_floor")

        with bottom_filter_cols[2]:
            st.info("筛选后的推荐结果会同步联动指标卡、地图热区、推荐卡片和下方表格，全部基于当前真实数据重新计算。")

    return start, end, selected_themes, selected_sources, top_n, score_floor


def _render_dashboard_insights_clean(filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> None:
    insight_col, table_col = st.columns([1.05, 1])
    with insight_col:
        st.markdown("### \u6295\u8bc9\u89c2\u5bdf")
        theme_counts = _theme_breakdown(filtered_complaints)
        if not theme_counts.empty:
            st.bar_chart(theme_counts.set_index("theme"))
        else:
            st.info("\u5f53\u524d\u7b5b\u9009\u6761\u4ef6\u4e0b\u6ca1\u6709\u53ef\u5c55\u793a\u7684\u6295\u8bc9\u5206\u5e03\u3002")

    with table_col:
        st.markdown("### \u63a8\u8350\u603b\u89c8")
        if recommendations.empty:
            st.info("\u5f53\u524d\u7b5b\u9009\u6761\u4ef6\u4e0b\u6ca1\u6709\u53ef\u5c55\u793a\u7684\u63a8\u8350\u7ed3\u679c\u3002")
        else:
            preview = recommendations.head(6).copy()
            st.dataframe(
                preview[
                    ["rank", "point_name", "source", "final_score", "risk_level", "filtered_complaint_count"]
                ].rename(
                    columns={
                        "rank": "\u6392\u540d",
                        "point_name": "\u70b9\u4f4d\u540d\u79f0",
                        "source": "\u7c7b\u578b",
                        "final_score": "\u7efc\u5408\u5f97\u5206",
                        "risk_level": "\u98ce\u9669\u7b49\u7ea7",
                        "filtered_complaint_count": "\u5468\u8fb9\u6295\u8bc9\u6570",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )


def _render_labeling_view_clean(bundle: DataBundle, recommendations: pd.DataFrame) -> None:
    st.markdown("### \u4eba\u5de5\u6807\u6ce8")
    label_file = manual_labels_path()
    existing_labels = read_manual_labels(label_file)
    label_stats = label_summary(existing_labels)
    st.caption(
        f"\u5f53\u524d\u5df2\u4fdd\u5b58\u6807\u6ce8 {label_stats['labeled_rows']} \u6761\uff0c\u6b63\u6837\u672c {label_stats['positive_labels']} \u6761\uff0c\u8d1f\u6837\u672c {label_stats['negative_labels']} \u6761\u3002"
    )

    label_editor = _prepare_label_editor_frame(bundle, recommendations).copy()
    label_editor["label"] = pd.to_numeric(label_editor["label"], errors="coerce")
    for col in ["point_id", "point_name", "source", "label_source", "label_notes", "labeled_by"]:
        if col in label_editor.columns:
            label_editor[col] = label_editor[col].fillna("").astype(str)
    if "labeled_at" in label_editor.columns:
        label_editor["labeled_at"] = pd.to_datetime(label_editor["labeled_at"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M:%S").fillna("")

    edited_labels = st.data_editor(
        label_editor,
        use_container_width=True,
        hide_index=True,
        height=420,
        column_config={
            "point_id": st.column_config.TextColumn("\u70b9\u4f4dID", disabled=True),
            "point_name": st.column_config.TextColumn("\u70b9\u4f4d\u540d\u79f0", disabled=True),
            "source": st.column_config.TextColumn("\u7c7b\u578b", disabled=True),
            "score": st.column_config.NumberColumn("\u5f53\u524d\u5f97\u5206", format="%.3f", disabled=True),
            "complaint_risk": st.column_config.NumberColumn("\u6295\u8bc9\u98ce\u9669", format="%.3f", disabled=True),
            "activity_proxy": st.column_config.NumberColumn("\u6d3b\u52a8\u4ee3\u7406", format="%.3f", disabled=True),
            "label": st.column_config.SelectboxColumn("\u4eba\u5de5\u6807\u7b7e", options=[None, 1, 0]),
            "label_source": st.column_config.TextColumn("\u6807\u7b7e\u6765\u6e90"),
            "label_notes": st.column_config.TextColumn("\u6807\u6ce8\u5907\u6ce8"),
            "labeled_by": st.column_config.TextColumn("\u6807\u6ce8\u4eba"),
            "labeled_at": st.column_config.TextColumn("\u6807\u6ce8\u65f6\u95f4"),
        },
    )

    action_cols = st.columns([1, 1, 1.2])
    with action_cols[0]:
        if st.button("\u4fdd\u5b58\u4eba\u5de5\u6807\u6ce8", use_container_width=True):
            save_manual_labels(edited_labels, label_file)
            st.session_state["label_action_result"] = {
                "mode": "saved",
                "path": str(label_file),
                "summary": label_summary(read_manual_labels(label_file)),
            }
    with action_cols[1]:
        if st.button("\u4fdd\u5b58\u5e76\u91cd\u8bad\u6a21\u578b", type="primary", use_container_width=True):
            st.session_state["label_action_result"] = _persist_labels_and_retrain(bundle, edited_labels)
    with action_cols[2]:
        _download_csv_button("\u4e0b\u8f7d\u6807\u6ce8\u6a21\u677f CSV", label_editor, "manual_labels_template.csv", key="clean-label-template")

    label_action_result = st.session_state.get("label_action_result")
    if not label_action_result:
        return
    if label_action_result.get("mode") == "saved":
        summary = label_action_result["summary"]
        st.success(f"\u5df2\u4fdd\u5b58\u4eba\u5de5\u6807\u6ce8\u3002\u5f53\u524d\u6709\u6548\u6807\u6ce8 {summary['labeled_rows']} \u6761\u3002")
    elif label_action_result.get("retrained"):
        metrics = label_action_result.get("metrics", {})
        st.success(
            f"\u5df2\u4fdd\u5b58\u6807\u6ce8\u5e76\u5b8c\u6210\u91cd\u8bad\u3002\u6a21\u578b\u6765\u6e90\uff1a{metrics.get('model_source')}\uff0c\u6709\u6548\u6807\u6ce8 {metrics.get('labeled_rows')} \u6761\u3002"
        )
    else:
        st.info("\u6807\u6ce8\u5df2\u4fdd\u5b58\uff0c\u4f46\u5f53\u524d\u8fd8\u6ca1\u6709\u8db3\u591f\u7684\u7279\u5f81\u6570\u636e\u7528\u4e8e\u91cd\u8bad\u3002")


def _render_dashboard_footer_clean(bundle: DataBundle, filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> None:
    st.markdown("### \u66f4\u591a\u5de5\u5177")
    with st.expander("\u5c55\u5f00\u4eba\u5de5\u6807\u6ce8\u3001\u6a21\u578b\u8bca\u65ad\u4e0e\u8bc1\u636e\u5bfc\u51fa", expanded=False):
        tabs = st.tabs(["\u4eba\u5de5\u6807\u6ce8", "\u6a21\u578b\u8bca\u65ad", "\u8bc1\u636e\u5bfc\u51fa"])
        with tabs[0]:
            _render_labeling_view_clean(bundle, recommendations)
        with tabs[1]:
            _render_model_view()
        with tabs[2]:
            _render_evidence_and_exports(bundle, filtered_complaints, recommendations)


def _render_page_nav() -> str:
    st.markdown("### 页面导航")
    return st.radio(
        "页面导航",
        options=["总览", "推荐详情"],
        horizontal=True,
        label_visibility="collapsed",
        key="dashboard_page_nav",
    )


def _render_overview_page(bundle: DataBundle, filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> None:
    metrics_frame = _build_homepage_metrics_clean(bundle, filtered_complaints, recommendations)
    _render_homepage_metric_band(metrics_frame)

    left_col, map_col, right_col = st.columns([0.9, 1.8, 1.05])
    with left_col:
        _render_summary_panel_clean(filtered_complaints, recommendations)
    with map_col:
        st.markdown("### 风险与推荐态势")
        st_folium(_build_map(filtered_complaints, recommendations), width=None, height=640, returned_objects=[])
    with right_col:
        _render_top_recommendation_cards_clean(recommendations)
        _download_csv_button("下载推荐结果 CSV", recommendations, "predictions_export.csv", key="clean-dashboard-predictions")


def _render_detail_page(bundle: DataBundle, filtered_complaints: pd.DataFrame, recommendations: pd.DataFrame) -> None:
    st.markdown("### 推荐详情")
    intro_cols = st.columns([1.2, 1, 1])
    intro_cols[0].info(f"当前筛选后共有 {len(recommendations)} 个候选点参与排序，均基于真实投诉数据和候选点位数据重新计算。")
    intro_cols[1].metric("Top1 推荐", "-" if recommendations.empty else str(recommendations.iloc[0]['point_name']))
    intro_cols[2].metric("平均得分", "-" if recommendations.empty else f"{pd.to_numeric(recommendations['final_score'], errors='coerce').mean():.3f}")

    _render_dashboard_insights_clean(filtered_complaints, recommendations)

    st.markdown("### 推荐清单")
    if recommendations.empty:
        st.info("当前筛选条件下没有可展示的推荐结果。")
    else:
        detail_table = recommendations[
            ["rank", "point_name", "source", "final_score", "risk_level", "filtered_complaint_count", "reason_1", "reason_2"]
        ].rename(
            columns={
                "rank": "排名",
                "point_name": "点位名称",
                "source": "类型",
                "final_score": "综合得分",
                "risk_level": "风险等级",
                "filtered_complaint_count": "周边投诉数",
                "reason_1": "核心理由",
                "reason_2": "补充说明",
            }
        )
        st.dataframe(detail_table, use_container_width=True, hide_index=True, height=380)
        _download_csv_button("导出当前推荐明细", recommendations, "predictions_export.csv", key="detail-page-export")

    _render_dashboard_footer_clean(bundle, filtered_complaints, recommendations)


def main() -> None:
    st.set_page_config(page_title="杨浦区地摊经济监测与点位决策支持平台", layout="wide")
    _render_shell_styles()
    bundle = load_bundle()
    _render_brand_header_clean(bundle)
    start, end, selected_themes, selected_sources, top_n, score_floor = _render_filter_panel_clean(bundle)
    active_page = _render_page_nav()

    filtered_complaints = _filter_complaints_by_theme(bundle.complaints, start, end, selected_themes)
    recommendations = build_display_recommendations(bundle, filtered_complaints)
    if selected_sources:
        recommendations = recommendations[recommendations["source"].isin(selected_sources)].copy()
    recommendations = recommendations[recommendations["final_score"] >= score_floor].copy()
    recommendations = recommendations.head(top_n).reset_index(drop=True)

    if active_page == "总览":
        _render_overview_page(bundle, filtered_complaints, recommendations)
    else:
        _render_detail_page(bundle, filtered_complaints, recommendations)


if __name__ == "__main__":
    main()
