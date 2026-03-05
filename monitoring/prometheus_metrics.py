from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter("api_requests_total", "Total API Requests")
INFERENCE_LATENCY = Histogram("inference_latency_seconds", "Model inference latency")
GEOFENCE_VIOLATIONS = Counter("geofence_violations_total", "Geofence breach events")
FATIGUE_ALERTS = Counter("fatigue_alerts_total", "Driver fatigue alerts")
DRIFT_EVENTS = Counter("drift_events_total", "Detected data drift events")
