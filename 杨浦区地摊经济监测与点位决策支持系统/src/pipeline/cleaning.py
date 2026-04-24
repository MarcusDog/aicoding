from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .amap_client import AmapClient


COMPLAINT_ALIASES = {
    "id": ["id"],
    "created_at": ["created_at", "create_time"],
    "category": ["category", "type"],
    "content": ["content", "desc"],
    "address": ["address"],
    "lon": ["lon", "lng", "longitude"],
    "lat": ["lat", "latitude"],
    "source": ["source"],
}

CANDIDATE_ALIASES = {
    "point_id": ["point_id", "id"],
    "point_name": ["point_name", "name"],
    "address": ["address"],
    "lon": ["lon", "lng", "longitude"],
    "lat": ["lat", "latitude"],
    "source": ["source"],
    "label": ["label", "suitability_label"],
    "label_source": ["label_source"],
}


@dataclass
class CleaningReport:
    total_rows: int
    deduplicated_rows: int
    dropped_short_text_rows: int
    geocoded_rows: int
    remaining_rows: int
    geo_coverage_ratio: float


def _rename_with_aliases(df: pd.DataFrame, aliases: dict[str, list[str]]) -> pd.DataFrame:
    rename_map: dict[str, str] = {}
    lower_map = {str(col).strip().lower(): col for col in df.columns}
    for target, candidates in aliases.items():
        for candidate in candidates:
            original = lower_map.get(candidate.strip().lower())
            if original is not None:
                rename_map[original] = target
                break
    return df.rename(columns=rename_map)


def _fill_missing_text(series: pd.Series, fallback: str) -> pd.Series:
    return series.fillna(fallback).astype(str).str.strip().replace("", fallback)


def _prepare_amap() -> AmapClient | None:
    api_key = os.getenv("AMAP_API_KEY", "").strip()
    if not api_key:
        return None
    return AmapClient(api_key)


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        normalized = str(value).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)
    return out


def _normalize_address_text(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    value = re.sub(r"^\d+[、.,．]\s*", "", value)
    value = value.replace("（", "(").replace("）", ")")
    value = re.sub(r"\s+", "", value)
    value = value.replace("上海市杨浦区", "").replace("杨浦区", "")
    value = re.sub(
        r"^(控江街道|江浦路街道|平凉街道|四平街道|大桥街道|五角场街道|定海路街道|定海街道|延吉新村街道|长白新村街道|长海路街道|殷行街道|新江湾城街道)",
        "",
        value,
    )
    return value.strip("，,；; ")


def _address_candidates(address: str, city_hint: str | None = None) -> list[str]:
    text = _normalize_address_text(address)
    if not text:
        return []
    if re.fullmatch(r"\d{1,2}[./月-]\d{1,2}(?:日)?(?:至\d{1,2}[./月-]\d{1,2}(?:日)?)?", text):
        return []

    pieces = [text]
    pieces.extend(part.strip() for part in re.split(r"[，；;。]", text) if part.strip())

    patterns = [
        r"([^\s，；。]{1,30}(?:路|街|大道|支路|巷)\d+号[^\s，；。]*)",
        r"([^\s，；。]{1,30}(?:路|街|大道|支路|巷)\d+弄[^\s，；。]*)",
        r"([^\s，；。]{1,20}(?:路|街|大道|支路|巷)与[^\s，；。]{1,20}(?:路|街|大道|支路|巷)交叉口)",
        r"([^\s，；。]{1,30}(?:地铁站|广场|小区|市场|商场|大厦|园区|学校|医院))",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, text):
            pieces.append(str(match).strip())

    trimmed: list[str] = []
    for piece in pieces:
        current = piece
        current = re.sub(r"(附近|周边|一带|区域内|区域)$", "", current).strip()
        current = re.sub(r"(内\d+号楼.*|南侧.*|北侧.*|东侧.*|西侧.*|楼顶.*|道路上.*|河道内.*)$", "", current).strip()
        current = re.sub(r"(存在.*|有居民.*|施工中.*|晚间.*|雨天.*)$", "", current).strip()
        if current:
            trimmed.append(current)

    prefixed: list[str] = []
    if city_hint:
        city_hint = str(city_hint).strip()
        prefixed = [f"{city_hint}{item}" for item in trimmed if not item.startswith(city_hint)]

    return _dedupe_preserve_order(trimmed + prefixed)


def _within_yangpu(lon: float, lat: float) -> bool:
    return 121.45 <= float(lon) <= 121.58 and 31.23 <= float(lat) <= 31.34


def clean_complaints(df: pd.DataFrame, city_hint: str | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    df = _rename_with_aliases(df.copy(), COMPLAINT_ALIASES)
    total_rows = len(df)

    if "id" not in df.columns:
        df["id"] = [f"complaint-{idx + 1:06d}" for idx in range(len(df))]
    if "source" not in df.columns:
        df["source"] = "unknown"

    for col in ["category", "content", "address", "source"]:
        if col not in df.columns:
            df[col] = ""
    if "lon" not in df.columns:
        df["lon"] = np.nan
    if "lat" not in df.columns:
        df["lat"] = np.nan
    if "created_at" not in df.columns:
        df["created_at"] = pd.NaT

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df[df["created_at"].notna()].copy()
    df["category"] = _fill_missing_text(df["category"], "未分类")
    df["content"] = _fill_missing_text(df["content"], "无文本")
    df["address"] = _fill_missing_text(df["address"], "地址缺失")

    before_dedup = len(df)
    df = df.drop_duplicates(subset=["id"], keep="first")
    deduplicated_rows = before_dedup - len(df)

    short_mask = df["content"].str.len() < 5
    dropped_short_text_rows = int(short_mask.sum())
    df = df[~short_mask].copy()

    geocoded_rows = 0
    amap = _prepare_amap()
    missing_geo = df["lon"].isna() | df["lat"].isna()
    if amap and missing_geo.any():
        for idx, row in df.loc[missing_geo, ["address"]].iterrows():
            if not row["address"] or row["address"] == "地址缺失":
                continue
            try:
                point = amap.resolve_address(
                    _address_candidates(str(row["address"]), city_hint),
                    city_hint,
                    validator=_within_yangpu,
                )
            except Exception:
                point = None
            if point:
                df.at[idx, "lon"] = point[0]
                df.at[idx, "lat"] = point[1]
                geocoded_rows += 1

    df["date"] = df["created_at"].dt.date.astype(str)
    df["hour_bucket"] = df["created_at"].dt.hour
    df["is_located"] = (~df["lon"].isna()) & (~df["lat"].isna())
    geo_coverage_ratio = float(df["is_located"].mean()) if len(df) else 0.0

    report = CleaningReport(
        total_rows=total_rows,
        deduplicated_rows=deduplicated_rows,
        dropped_short_text_rows=dropped_short_text_rows,
        geocoded_rows=geocoded_rows,
        remaining_rows=len(df),
        geo_coverage_ratio=geo_coverage_ratio,
    )
    return df, report.__dict__


def clean_candidate_points(df: pd.DataFrame, city_hint: str | None = None) -> pd.DataFrame:
    df = _rename_with_aliases(df.copy(), CANDIDATE_ALIASES)
    if "point_id" not in df.columns:
        df["point_id"] = [f"point-{idx + 1:03d}" for idx in range(len(df))]
    for col in ["point_name", "address", "source", "label", "label_source"]:
        if col not in df.columns:
            df[col] = ""
    if "lon" not in df.columns:
        df["lon"] = np.nan
    if "lat" not in df.columns:
        df["lat"] = np.nan

    df["point_name"] = _fill_missing_text(df["point_name"], "未命名点位")
    df["source"] = _fill_missing_text(df["source"], "unknown")

    amap = _prepare_amap()
    missing_geo = (df["lon"].isna() | df["lat"].isna()) & df["address"].astype(str).str.strip().ne("")
    if amap and missing_geo.any():
        for idx, row in df.loc[missing_geo, ["address"]].iterrows():
            try:
                point = amap.resolve_address(
                    _address_candidates(str(row["address"]), city_hint),
                    city_hint,
                    validator=_within_yangpu,
                )
            except Exception:
                point = None
            if point:
                df.at[idx, "lon"] = point[0]
                df.at[idx, "lat"] = point[1]

    df = df[df["lon"].notna() & df["lat"].notna()].copy()
    if "label" in df.columns:
        df["label"] = pd.to_numeric(df["label"], errors="coerce")
    return df


def clean_calendar(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.date.astype(str)
    out["is_holiday"] = out["is_holiday"].fillna(0).astype(int)
    out["is_weekend"] = out["is_weekend"].fillna(0).astype(int)
    if "holiday_name" not in out.columns:
        out["holiday_name"] = ""
    if "source" not in out.columns:
        out["source"] = "unknown"
    return out.dropna(subset=["date"]).copy()


def clean_weather(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.date.astype(str)
    if "weather_text" not in out.columns:
        out["weather_text"] = ""
    if "temp_low" not in out.columns:
        out["temp_low"] = np.nan
    if "temp_high" not in out.columns:
        out["temp_high"] = np.nan
    if "source" not in out.columns:
        out["source"] = "unknown"
    return out.dropna(subset=["date"]).copy()
