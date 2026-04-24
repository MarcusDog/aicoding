from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fraud_detection.inference import feature_schema, load_bundle, predict_records  # noqa: E402
from fraud_detection.settings import METRICS_DIR, MODELS_DIR  # noqa: E402


class PredictRequest(BaseModel):
    transaction_id: str | None = None
    features: dict[str, float] = Field(default_factory=dict, description="Feature dict keyed by model feature names.")


class BatchPredictRequest(BaseModel):
    records: list[PredictRequest]


app = FastAPI(title="Fraud Detection API", version="0.1.0")


@lru_cache(maxsize=1)
def _load_model_bundle() -> dict[str, Any] | None:
    model_path = MODELS_DIR / "best_model.joblib"
    if not model_path.exists():
        return None
    return load_bundle(model_path)


@app.get("/health")
def health():
    bundle = _load_model_bundle()
    return {"status": "ok", "model_loaded": bundle is not None, "version": app.version}


@app.get("/metrics")
def metrics():
    metrics_path = METRICS_DIR / "best_metrics.json"
    if not metrics_path.exists():
        raise HTTPException(status_code=404, detail="Metrics not found. Train the model first.")
    return json.loads(metrics_path.read_text(encoding="utf-8"))


@app.get("/schema")
def schema():
    bundle = _load_model_bundle()
    if bundle is None:
        raise HTTPException(status_code=404, detail="Model not found. Train the model first.")
    return feature_schema(bundle)


@app.post("/predict")
def predict(payload: PredictRequest):
    bundle = _load_model_bundle()
    if bundle is None:
        raise HTTPException(status_code=404, detail="Model not found. Train the model first.")
    record = {"transaction_id": payload.transaction_id, **payload.features}
    try:
        return predict_records(bundle, [record])[0]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/predict/batch")
def predict_batch(payload: BatchPredictRequest):
    bundle = _load_model_bundle()
    if bundle is None:
        raise HTTPException(status_code=404, detail="Model not found. Train the model first.")
    records = [{"transaction_id": item.transaction_id, **item.features} for item in payload.records]
    try:
        results = predict_records(bundle, records)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"total": len(results), "fraud_count": int(sum(item["is_fraud"] for item in results)), "results": results}
