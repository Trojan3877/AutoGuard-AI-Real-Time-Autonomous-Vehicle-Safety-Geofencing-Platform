"""Basic smoke tests that validate moved modules are importable and core logic works."""

import sys
import os

# Ensure repo root is on PYTHONPATH when running pytest directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_geofence_haversine():
    from libs.geofence.google_maps_geofence import haversine, is_inside_geofence

    # Same point → distance 0
    assert haversine(0, 0, 0, 0) == 0.0

    # Two well-known cities: London (51.5, -0.12) → Paris (48.85, 2.35) ≈ 340 km
    distance = haversine(51.5, -0.12, 48.85, 2.35)
    assert 300_000 < distance < 400_000, f"Expected ~340 km, got {distance}"


def test_geofence_inside():
    from libs.geofence.google_maps_geofence import is_inside_geofence

    center_lat, center_lng = 37.7749, -122.4194
    radius = 5000  # 5 km

    # Point at center should be inside
    assert is_inside_geofence(center_lat, center_lng, center_lat, center_lng, radius)

    # Point very far away should be outside
    assert not is_inside_geofence(0.0, 0.0, center_lat, center_lng, radius)


def test_drift_detection():
    import numpy as np
    from libs.pipelines.drift_detection import detect_drift

    # Identical distributions → no drift
    data = np.random.normal(0, 1, 1000)
    assert not detect_drift(data, data + 0.001)

    # Very different distributions → drift detected
    ref = np.random.normal(0, 1, 1000)
    live = np.random.normal(10, 1, 1000)
    assert detect_drift(ref, live)


def test_model_registry():
    from libs.models.model_registry import ModelRegistry

    reg = ModelRegistry()
    reg.register("v1", object())
    reg.register("v2", object())

    assert "v1" in reg.list_versions()
    assert "v2" in reg.list_versions()
    assert reg.get("v3") is None


def test_ear_metric():
    import numpy as np
    from libs.models.ear_metric import compute_ear

    # Build a simple set of 6 eye points (roughly open eye)
    pts = np.array([
        [0.0, 0.0],   # p0
        [1.0, 1.0],   # p1
        [2.0, 1.0],   # p2
        [3.0, 0.0],   # p3
        [2.0, -1.0],  # p4
        [1.0, -1.0],  # p5
    ])
    ear = compute_ear(pts)
    assert ear > 0, "EAR should be positive"
