from __future__ import annotations

import ast
from typing import Any

import numpy as np
import pandas as pd

from fraud_detection.inference import summarize_reasons


def _reference_scores(prediction_frame: pd.DataFrame, stream_frame: pd.DataFrame) -> np.ndarray:
    if not prediction_frame.empty and "fraud_score" in prediction_frame.columns:
        scores = prediction_frame["fraud_score"].dropna().astype(float).to_numpy()
    elif not stream_frame.empty and "fraud_score" in stream_frame.columns:
        scores = stream_frame["fraud_score"].dropna().astype(float).to_numpy()
    else:
        scores = np.array([0.0, 1.0], dtype=float)
    scores = np.sort(scores)
    if len(scores) == 0:
        return np.array([0.0, 1.0], dtype=float)
    return scores


def _risk_index(scores: pd.Series, reference_scores: np.ndarray) -> np.ndarray:
    numeric_scores = scores.fillna(0).astype(float).to_numpy()
    denominator = max(len(reference_scores), 1)
    percentiles = np.searchsorted(reference_scores, numeric_scores, side="right") / denominator * 100
    return np.clip(np.round(percentiles, 1), 0, 100)


def _display_risk_level(risk_index: pd.Series) -> pd.Series:
    levels = pd.cut(
        risk_index,
        bins=[-0.1, 55, 80, 100],
        labels=["low", "medium", "high"],
        include_lowest=True,
    )
    return levels.astype(str)


def _normalize_reason(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "特征偏离较小"
    if isinstance(value, list):
        parts = value
    elif isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            parts = parsed if isinstance(parsed, list) else [value]
        except (SyntaxError, ValueError):
            parts = [value]
    else:
        parts = [str(value)]
    return " | ".join(str(item).replace("deviation=", "偏离 ") for item in parts)


def _decorate_frame(
    frame: pd.DataFrame,
    reference_scores: np.ndarray,
    source: str,
    bundle: dict[str, Any] | None = None,
) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "transaction_id",
                "source",
                "fraud_score",
                "risk_index",
                "display_risk_level",
                "actual_label",
                "predicted_positive",
                "reason_display",
            ]
        )

    view = frame.copy().reset_index(drop=True)
    if "transaction_id" not in view.columns:
        view["transaction_id"] = [f"test-{index:06d}" for index in range(len(view))]
    if "actual_label" not in view.columns:
        if "label" in view.columns:
            view["actual_label"] = view["label"]
        elif "Class" in view.columns:
            view["actual_label"] = view["Class"]
        else:
            view["actual_label"] = 0
    if "predicted_positive" not in view.columns:
        if "is_fraud" in view.columns:
            view["predicted_positive"] = view["is_fraud"].astype(int)
        elif "predicted_class" in view.columns:
            view["predicted_positive"] = view["predicted_class"].astype(int)
        else:
            view["predicted_positive"] = 0

    view["source"] = source
    view["risk_index"] = _risk_index(view["fraud_score"], reference_scores)
    view["display_risk_level"] = _display_risk_level(view["risk_index"])

    if "reason" in view.columns:
        view["reason_display"] = view["reason"].map(_normalize_reason)
    elif bundle and bundle.get("feature_columns"):
        feature_columns = [column for column in bundle["feature_columns"] if column in view.columns]
        if feature_columns:
            view["reason_display"] = [
                _normalize_reason(
                    summarize_reasons(row[feature_columns], bundle.get("feature_summary", {}))
                )
                for _, row in view.iterrows()
            ]
        else:
            view["reason_display"] = "模型识别为高风险样本"
    else:
        view["reason_display"] = "模型识别为高风险样本"

    return view


def build_dashboard_frame(
    stream_frame: pd.DataFrame,
    prediction_frame: pd.DataFrame,
    limit: int = 30,
) -> pd.DataFrame:
    reference_scores = _reference_scores(prediction_frame, stream_frame)
    if not stream_frame.empty and "fraud_score" in stream_frame.columns:
        dashboard = _decorate_frame(stream_frame.head(limit), reference_scores, source="实时批次")
    elif not prediction_frame.empty and "fraud_score" in prediction_frame.columns:
        dashboard = _decorate_frame(
            prediction_frame.sort_values("fraud_score", ascending=False).head(limit),
            reference_scores,
            source="离线测试",
        )
    else:
        dashboard = pd.DataFrame()
    return dashboard


def build_case_frame(
    stream_frame: pd.DataFrame,
    prediction_frame: pd.DataFrame,
    bundle: dict[str, Any],
    limit: int = 20,
) -> pd.DataFrame:
    reference_scores = _reference_scores(prediction_frame, stream_frame)
    frames: list[pd.DataFrame] = []

    if not prediction_frame.empty and "fraud_score" in prediction_frame.columns:
        offline_top = prediction_frame.sort_values("fraud_score", ascending=False).head(max(limit // 2, 8))
        frames.append(_decorate_frame(offline_top, reference_scores, source="离线测试", bundle=bundle))

    if not stream_frame.empty and "fraud_score" in stream_frame.columns:
        stream_top = stream_frame.sort_values("fraud_score", ascending=False).head(max(limit // 2, 8))
        frames.append(_decorate_frame(stream_top, reference_scores, source="实时批次", bundle=bundle))

    if not frames:
        return pd.DataFrame()

    merged = pd.concat(frames, ignore_index=True)
    merged = merged.sort_values(["risk_index", "fraud_score"], ascending=[False, False]).head(limit)
    return merged.reset_index(drop=True)


def build_dashboard_summary(frame: pd.DataFrame, batch_id: int | str | None) -> dict[str, Any]:
    if frame.empty:
        return {
            "batch_id": batch_id or "-",
            "event_count": 0,
            "high_risk_count": 0,
            "average_risk_index": 0.0,
        }
    return {
        "batch_id": batch_id or "-",
        "event_count": int(len(frame)),
        "high_risk_count": int((frame["display_risk_level"] == "high").sum()),
        "average_risk_index": round(float(frame["risk_index"].mean()), 1),
    }
