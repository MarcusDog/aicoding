from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ..config import Config


def write_json(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def dataframe_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []
    object_frame = df.astype(object)
    return object_frame.where(pd.notna(object_frame), None).to_dict(orient="records")


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def write_analysis_outputs(results: dict[str, Any]) -> None:
    for key in ("news_cleaned", "hot_topics", "keyword_trends", "event_clusters", "sentiment_results", "alerts"):
        value = results.get(key)
        if isinstance(value, pd.DataFrame):
            write_parquet(value, Config.PROCESSED_DIR / f"{key}.parquet")
            write_json(dataframe_to_records(value), Config.PROCESSED_DIR / f"{key}.json")
