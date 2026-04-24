from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def raw_dir() -> Path:
    return ensure_dir(project_root() / "data" / "raw")


def processed_dir() -> Path:
    return ensure_dir(project_root() / "data" / "processed")


def artifacts_dir() -> Path:
    return ensure_dir(project_root() / "artifacts")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    ensure_dir(path.parent)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def write_json(payload: dict[str, Any], path: Path) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def file_metadata(path: Path) -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": str(path),
        "exists": exists,
        "size_bytes": path.stat().st_size if exists else None,
        "last_modified": path.stat().st_mtime if exists else None,
    }
