from fastapi import FastAPI
from geofence import check_geofence
from mlops.prometheus_metrics import request_counter

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "running"}

@app.post("/predict")
def predict(data: dict):
    request_counter.inc()
    geofence_status = check_geofence(data["lat"], data["lon"])
    return {"geofence_valid": geofence_status}
