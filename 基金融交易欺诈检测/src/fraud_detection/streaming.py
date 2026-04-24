from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from fraud_detection.inference import predict_records


def stream_event_schema(feature_columns: list[str]) -> dict[str, str]:
    schema = {
        "transaction_id": "string",
        "event_time": "string",
        "label": "int",
    }
    schema.update({column: "double" for column in feature_columns})
    return schema


def score_micro_batch(
    bundle: dict[str, Any],
    batch_df,
    output_dir: Path,
    batch_id: int,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf = batch_df.toPandas()
    if pdf.empty:
        return {"batch_id": batch_id, "event_count": 0}

    records = pdf.to_dict(orient="records")
    results = predict_records(bundle, records)
    result_frame = pd.DataFrame(results)

    keep_columns = ["transaction_id", "event_time", "label"] + bundle["feature_columns"]
    available_columns = [column for column in keep_columns if column in pdf.columns]
    merged = pd.concat(
        [
            pdf[available_columns].reset_index(drop=True),
            result_frame.reset_index(drop=True),
        ],
        axis=1,
    )
    merged["processed_at"] = datetime.now(timezone.utc).isoformat()
    return persist_stream_results(merged, output_dir, batch_id=batch_id)


def build_stream_summary(frame: pd.DataFrame, batch_id: int) -> dict[str, Any]:
    fraud_hits = int(frame["is_fraud"].sum()) if "is_fraud" in frame.columns else 0
    avg_score = float(frame["fraud_score"].mean()) if "fraud_score" in frame.columns else 0.0
    high_risk = int((frame["risk_level"] == "high").sum()) if "risk_level" in frame.columns else 0
    return {
        "batch_id": batch_id,
        "event_count": int(len(frame)),
        "fraud_hits": fraud_hits,
        "high_risk_count": high_risk,
        "average_score": avg_score,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }


def persist_stream_results(frame: pd.DataFrame, output_dir: Path, batch_id: int) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    events_path = output_dir / "scored_events.jsonl"
    with events_path.open("a", encoding="utf-8") as handle:
        for row in frame.to_dict(orient="records"):
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = build_stream_summary(frame, batch_id=batch_id)
    (output_dir / "latest_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    frame.tail(min(200, len(frame))).to_csv(output_dir / "latest_batch.csv", index=False, encoding="utf-8-sig")
    return summary


def load_stream_outputs(output_dir: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    latest_batch_path = output_dir / "latest_batch.csv"
    summary_path = output_dir / "latest_summary.json"
    frame = pd.read_csv(latest_batch_path) if latest_batch_path.exists() else pd.DataFrame()
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}
    return frame, summary
