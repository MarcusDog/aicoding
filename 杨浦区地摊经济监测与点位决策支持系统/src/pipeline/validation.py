from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .io_utils import file_metadata


REQUIRED_INPUTS = {
    "complaints.csv": {"required_any": ["address", "lon", "lat"], "required_all": ["created_at", "category", "content"]},
    "candidate_points.csv": {"required_all": ["point_name"], "required_any": ["address", "lon", "lat"]},
    "calendar.csv": {"required_all": ["date", "is_holiday", "is_weekend"]},
    "weather.csv": {"required_all": ["date", "weather_code"]},
}


def _normalize_columns(columns: list[str]) -> set[str]:
    return {str(col).strip().lower() for col in columns}


def validate_csv_schema(path: Path, rules: dict[str, list[str]]) -> dict[str, Any]:
    result: dict[str, Any] = {"file": path.name, "status": "ok", "errors": [], "warnings": []}
    if not path.exists():
        result["status"] = "missing"
        result["errors"].append("file not found")
        return result

    df = pd.read_csv(path, nrows=3)
    cols = _normalize_columns(df.columns.tolist())
    required_all = [c.lower() for c in rules.get("required_all", [])]
    missing_all = [c for c in required_all if c not in cols]
    if missing_all:
        result["status"] = "invalid"
        result["errors"].append(f"missing required columns: {', '.join(missing_all)}")

    required_any = [c.lower() for c in rules.get("required_any", [])]
    if required_any and not any(col in cols for col in required_any):
        result["status"] = "invalid"
        result["errors"].append(f"need at least one of: {', '.join(required_any)}")

    if len(df.columns) == 0:
        result["status"] = "invalid"
        result["errors"].append("empty header")

    return result


def build_validation_report(raw_dir: Path) -> dict[str, Any]:
    files: dict[str, Any] = {}
    statuses = []
    for filename, rules in REQUIRED_INPUTS.items():
        path = raw_dir / filename
        status = validate_csv_schema(path, rules)
        status["metadata"] = file_metadata(path)
        statuses.append(status["status"])
        files[filename] = status

    overall = "ok"
    if "invalid" in statuses:
        overall = "invalid"
    elif "missing" in statuses:
        overall = "incomplete"

    return {"overall_status": overall, "files": files}
