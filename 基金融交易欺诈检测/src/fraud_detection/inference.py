from __future__ import annotations

from typing import Any

import joblib
import pandas as pd


def load_bundle(model_path):
    return joblib.load(model_path)


def predict_records(bundle: dict[str, Any], records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feature_columns = bundle["feature_columns"]
    threshold = float(bundle["threshold"])
    frame = pd.DataFrame(records)
    missing = [column for column in feature_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required features: {missing}")

    ordered = frame[feature_columns].astype(float)
    scores = bundle["estimator"].predict_proba(ordered)[:, 1]
    results = []
    for idx, score in enumerate(scores):
        results.append(
            {
                "transaction_id": records[idx].get("transaction_id", f"row_{idx}"),
                "fraud_score": float(score),
                "threshold": threshold,
                "is_fraud": bool(score >= threshold),
                "risk_level": score_to_risk_level(float(score), threshold),
                "reason": summarize_reasons(ordered.iloc[idx], bundle.get("feature_summary", {})),
            }
        )
    return results


def feature_schema(bundle: dict[str, Any]) -> dict[str, Any]:
    feature_columns = bundle["feature_columns"]
    sample = {}
    for feature_name in feature_columns:
        summary = bundle.get("feature_summary", {}).get(feature_name, {})
        sample[feature_name] = summary.get("median", 0.0)
    return {
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "sample_features": sample,
    }


def score_to_risk_level(score: float, threshold: float) -> str:
    if score >= max(0.9, threshold):
        return "high"
    if score >= max(0.6, threshold * 0.8):
        return "medium"
    return "low"


def summarize_reasons(record: pd.Series, feature_summary: dict[str, dict[str, float]]) -> list[str]:
    deviations = []
    for feature_name, value in record.items():
        summary = feature_summary.get(feature_name)
        if not summary:
            continue
        deviation = abs(float(value) - summary["median"]) / summary["iqr"]
        deviations.append((deviation, feature_name))
    deviations.sort(reverse=True)
    return [f"{feature} deviation={deviation:.2f}" for deviation, feature in deviations[:3]]
