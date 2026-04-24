from fastapi.testclient import TestClient

from api.main import app


def test_health_endpoint_returns_expected_shape() -> None:
    client = TestClient(app)
    response = client.get("/api/system/health")
    assert response.status_code == 200
    payload = response.json()
    assert {"status", "tables", "startup_steps"}.issubset(payload.keys())


def test_volatility_forecast_endpoint_is_available() -> None:
    client = TestClient(app)
    response = client.get("/api/analysis/volatility-forecast", params={"product_id": "IF", "limit": 10})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
