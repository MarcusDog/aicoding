import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "model_loaded" in payload


def test_metrics_endpoint_when_model_exists():
    metrics_path = Path("artifacts/metrics/best_metrics.json")
    if not metrics_path.exists():
        return

    client = TestClient(app)
    response = client.get("/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert "pr_auc" in payload


def test_schema_endpoint_when_model_exists():
    model_path = Path("models/best_model.joblib")
    if not model_path.exists():
        return

    client = TestClient(app)
    response = client.get("/schema")
    assert response.status_code == 200
    payload = response.json()
    assert payload["feature_count"] > 0
    assert isinstance(payload["sample_features"], dict)
