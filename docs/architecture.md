# Architecture – AutoGuard AI

## Overview

AutoGuard AI is a real-time autonomous vehicle safety and geofencing platform.  
It ingests live telemetry from vehicle sensors, runs AI-based perception and fatigue models, enforces geofencing policies, and exposes results via REST and gRPC APIs with a Streamlit control-centre dashboard.

## Component map

```
┌─────────────────────────────────────────────────────────────────┐
│                      Vehicle / Sensor Fleet                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │ Kafka (vehicle_telemetry topic)
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  libs/streaming  –  Kafka producer / consumer                │
└───────────────────────────┬──────────────────────────────────┘
                            │
               ┌────────────┴────────────┐
               ▼                         ▼
  ┌─────────────────────┐    ┌─────────────────────────┐
  │  libs/perception    │    │  libs/models (fatigue)  │
  │  CNN / ViT model    │    │  CNN / LSTM / EAR metric│
  └──────────┬──────────┘    └────────────┬────────────┘
             │                            │
             └────────────┬───────────────┘
                          ▼
            ┌─────────────────────────┐
            │   libs/risk-engine-cpp  │
            │   C++ risk calculator   │
            └────────────┬────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
 ┌──────────────────┐    ┌──────────────────────┐
 │  services/api    │    │  libs/geofence        │
 │  FastAPI + gRPC  │    │  Haversine geofence   │
 │  Redis cache     │    └──────────────────────┘
 │  A/B routing     │
 │  Load balancer   │
 └────────┬─────────┘
          │
          ▼
 ┌──────────────────┐
 │  apps/dashboard  │
 │  Streamlit UI    │
 │  WebSocket feed  │
 └──────────────────┘
          │
          ▼
 ┌──────────────────────────┐
 │  libs/monitoring         │
 │  Prometheus metrics      │
 │  OpenTelemetry tracing   │
 └──────────────────────────┘
```

## Data flow (step-by-step)

1. **Sensor data generation** – `scripts/generate_data.py` or `libs/streaming/kafka_producer.py` generates/streams vehicle telemetry (speed, GPS, eye-aspect-ratio).
2. **Kafka ingestion** – `libs/streaming/kafka_consumer.py` consumes the `vehicle_telemetry` topic.
3. **Perception inference** – `libs/perception` runs CNN/ViT models (CUDA-accelerated) to detect obstacles, pedestrians, and vehicles.
4. **Fatigue detection** – `libs/models` evaluates eye-aspect-ratio and runs CNN/LSTM classifiers to detect driver fatigue.
5. **Risk scoring** – `libs/risk-engine-cpp` computes a risk score from speed and obstacle distance.
6. **Geofence check** – `libs/geofence` validates GPS coordinates against the allowed zone.
7. **API response** – `services/api` (FastAPI + gRPC) returns safety status, caches results in Redis, routes via A/B testing.
8. **Dashboard** – `apps/dashboard` streams real-time telemetry and alerts via WebSocket + Streamlit.
9. **Observability** – Prometheus metrics + OpenTelemetry spans are emitted throughout.
10. **Infrastructure** – Kubernetes HPA scales pods on CPU load; Terraform provisions AWS EKS + ECR.

## Key technology choices

| Concern | Technology | Reason |
|---|---|---|
| Streaming | Apache Kafka | Durable, high-throughput telemetry ingestion |
| Caching | Redis | Deduplicates repeated inference calls, cuts compute |
| REST API | FastAPI (Python) | Async, automatic OpenAPI docs, Pydantic validation |
| High-perf RPC | gRPC | Low-latency binary protocol for inference under load |
| Perception | PyTorch (CNN + ViT) | GPU-accelerated, flexible model definitions |
| Risk score | C++ shared library | Deterministic, microsecond-latency calculation |
| RL simulation | Stable-Baselines3 / Gymnasium | Rapid policy experimentation |
| Dashboard | Streamlit + WebSocket | Fast iteration on real-time UI |
| Observability | Prometheus + OpenTelemetry | Industry-standard metrics + distributed tracing |
| Orchestration | Kubernetes + Helm + HPA | Auto-scaling for variable vehicle fleet load |
| IaC | Terraform (AWS) | Reproducible cloud infrastructure |
