"""Tests for the FastAPI endpoints in services/api/main.py."""

from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)


def test_liveness_probe():
    response = client.get("/health/live")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "alive"
    assert "uptime_seconds" in body


def test_readiness_probe():
    response = client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"


def test_legacy_health_endpoint():
    """The /health path must remain functional for backward compatibility."""
    response = client.get("/health")
    assert response.status_code == 200


def test_predict_valid_payload():
    """A well-formed request must return 200 with the expected schema."""
    payload = {"lat": 40.0, "lon": -83.0, "speed": 10.0, "vehicle_id": "VH-001"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "vehicle_id" in body
    assert body["vehicle_id"] == "VH-001"
    assert "geofence_valid" in body
    assert "latency_ms" in body


def test_predict_missing_vehicle_id():
    """Requests missing required fields must return 422 Unprocessable Entity."""
    payload = {"lat": 40.0, "lon": -83.0}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_invalid_lat():
    """Latitude out of range [-90, 90] must be rejected."""
    payload = {"lat": 200.0, "lon": -83.0, "vehicle_id": "VH-002"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_invalid_lon():
    """Longitude out of range [-180, 180] must be rejected."""
    payload = {"lat": 40.0, "lon": 999.0, "vehicle_id": "VH-003"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
