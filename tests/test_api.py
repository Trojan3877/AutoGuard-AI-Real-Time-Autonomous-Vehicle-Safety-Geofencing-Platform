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


def test_health_uptime_is_non_negative():
    """Uptime must be >= 0."""
    response = client.get("/health/live")
    assert response.json()["uptime_seconds"] >= 0


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


def test_predict_latency_is_non_negative():
    """latency_ms must always be a non-negative number."""
    payload = {"lat": 40.0, "lon": -83.0, "speed": 0.0, "vehicle_id": "VH-LAT"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert response.json()["latency_ms"] >= 0


def test_predict_geofence_valid_is_bool():
    """geofence_valid must be a boolean."""
    payload = {"lat": 40.0, "lon": -83.0, "vehicle_id": "VH-BOOL"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    assert isinstance(response.json()["geofence_valid"], bool)


def test_predict_missing_vehicle_id():
    """Requests missing required fields must return 422 Unprocessable Entity."""
    payload = {"lat": 40.0, "lon": -83.0}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_empty_vehicle_id():
    """An empty-string vehicle_id violates the min_length=1 constraint."""
    payload = {"lat": 40.0, "lon": -83.0, "vehicle_id": ""}
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


def test_predict_negative_speed_rejected():
    """Negative speed violates the ge=0 constraint and must be rejected."""
    payload = {"lat": 40.0, "lon": -83.0, "speed": -5.0, "vehicle_id": "VH-NEG"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_predict_boundary_lat_max():
    """Latitude exactly at upper bound (90) must be accepted."""
    payload = {"lat": 90.0, "lon": 0.0, "vehicle_id": "VH-MAXLAT"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200


def test_predict_boundary_lat_min():
    """Latitude exactly at lower bound (-90) must be accepted."""
    payload = {"lat": -90.0, "lon": 0.0, "vehicle_id": "VH-MINLAT"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200


def test_predict_boundary_lon_max():
    """Longitude exactly at upper bound (180) must be accepted."""
    payload = {"lat": 0.0, "lon": 180.0, "vehicle_id": "VH-MAXLON"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200


def test_predict_boundary_lon_min():
    """Longitude exactly at lower bound (-180) must be accepted."""
    payload = {"lat": 0.0, "lon": -180.0, "vehicle_id": "VH-MINLON"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200


def test_metrics_endpoint():
    """The /metrics endpoint must return Prometheus exposition text."""
    response = client.get("/metrics")
    assert response.status_code == 200
    # Prometheus format always contains the TYPE comment
    assert "api_requests_total" in response.text


def test_request_id_header_present():
    """Every response must carry the X-Request-ID header injected by middleware."""
    response = client.get("/health/live")
    assert "x-request-id" in response.headers


def test_predict_increments_request_counter():
    """Two successive /predict calls should increment the counter at least once."""
    from prometheus_client import REGISTRY
    before = REGISTRY.get_sample_value("api_requests_total") or 0.0
    payload = {"lat": 40.0, "lon": -83.0, "vehicle_id": "VH-CTR"}
    client.post("/predict", json=payload)
    after = REGISTRY.get_sample_value("api_requests_total") or 0.0
    assert after > before
