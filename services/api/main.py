import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .geofence import check_geofence
from libs.monitoring.prometheus_metrics import REQUEST_COUNT as request_counter

app = FastAPI(
    title="AutoGuard AI",
    description="Real-Time Autonomous Vehicle Safety & Geofencing Platform",
    version="0.1.0",
)

_START_TIME = time.time()


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class TelemetryRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Vehicle latitude")
    lon: float = Field(..., ge=-180, le=180, description="Vehicle longitude")
    speed: float = Field(0.0, ge=0, description="Vehicle speed in m/s")
    vehicle_id: str = Field(..., min_length=1, description="Unique vehicle identifier")


class PredictionResponse(BaseModel):
    vehicle_id: str
    geofence_valid: bool
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float


# ---------------------------------------------------------------------------
# Health endpoints (used by Kubernetes liveness / readiness / startup probes)
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["health"])
@app.get("/health/live", response_model=HealthResponse, tags=["health"])
def liveness():
    """Kubernetes liveness probe – confirms the process is alive."""
    return HealthResponse(
        status="alive",
        uptime_seconds=round(time.time() - _START_TIME, 2),
    )


@app.get("/health/ready", response_model=HealthResponse, tags=["health"])
def readiness():
    """Kubernetes readiness probe – confirms the service can handle traffic."""
    return HealthResponse(
        status="ready",
        uptime_seconds=round(time.time() - _START_TIME, 2),
    )


# ---------------------------------------------------------------------------
# Inference endpoint
# ---------------------------------------------------------------------------

@app.post("/predict", response_model=PredictionResponse, tags=["inference"])
def predict(body: TelemetryRequest):
    """Validate vehicle telemetry against the active geofence and run inference."""
    t0 = time.time()
    request_counter.inc()
    try:
        geofence_valid = check_geofence(body.lat, body.lon)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Geofence check failed: {exc}") from exc
    latency_ms = round((time.time() - t0) * 1000, 3)
    return PredictionResponse(
        vehicle_id=body.vehicle_id,
        geofence_valid=geofence_valid,
        latency_ms=latency_ms,
    )
