from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from fraud_detection.inference import feature_schema, load_bundle
from fraud_detection.settings import METRICS_DIR, MODELS_DIR, STREAMING_DIR
from fraud_detection.streaming import load_stream_outputs


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class SiteState:
    bundle: dict[str, Any]
    schema: dict[str, Any]
    metrics: dict[str, Any]
    training_summary: dict[str, Any]
    stream_frame: pd.DataFrame
    stream_summary: dict[str, Any]
    prediction_frame: pd.DataFrame


@lru_cache(maxsize=1)
def _load_bundle_cached() -> dict[str, Any]:
    model_path = MODELS_DIR / "best_model.joblib"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    return load_bundle(model_path)


def load_site_state() -> SiteState:
    metrics_path = METRICS_DIR / "best_metrics.json"
    predictions_path = METRICS_DIR / "test_predictions.csv"
    training_summary_path = METRICS_DIR / "training_summary.json"

    bundle = _load_bundle_cached()
    schema = feature_schema(bundle)
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    training_summary = json.loads(training_summary_path.read_text(encoding="utf-8")) if training_summary_path.exists() else {}
    stream_frame, stream_summary = load_stream_outputs(STREAMING_DIR)
    prediction_frame = pd.read_csv(predictions_path) if predictions_path.exists() else pd.DataFrame()
    return SiteState(
        bundle=bundle,
        schema=schema,
        metrics=metrics,
        training_summary=training_summary,
        stream_frame=stream_frame,
        stream_summary=stream_summary,
        prediction_frame=prediction_frame,
    )
