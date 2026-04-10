# AutoGuard AI – Real-Time Autonomous Vehicle Safety & Geofencing Platform

![CI](https://github.com/Trojan3877/AutoGuard-AI-Real-Time-Autonomous-Vehicle-Safety-Geofencing-Platform/actions/workflows/ci.yml/badge.svg)
![Docker](https://img.shields.io/badge/Docker-GPU_Ready-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-AutoScaling-326CE5?logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-Deployment-0F1689?logo=helm&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-Streaming-black?logo=apachekafka)
![Redis](https://img.shields.io/badge/Redis-Caching-red?logo=redis)
![gRPC](https://img.shields.io/badge/gRPC-High_Performance-blue)
![WebSockets](https://img.shields.io/badge/WebSocket-RealTime-green)
![Prometheus](https://img.shields.io/badge/Monitoring-Prometheus-orange?logo=prometheus)
![OpenTelemetry](https://img.shields.io/badge/Tracing-OpenTelemetry-5E5CE6)
![Locust](https://img.shields.io/badge/Load_Testing-Locust-00B894)
![GPU](https://img.shields.io/badge/GPU-Accelerated-76B900?logo=nvidia)
![License](https://img.shields.io/github/license/Trojan3877/AutoGuard-AI-Real-Time-Autonomous-Vehicle-Safety-Geofencing-Platform)
![Last Commit](https://img.shields.io/github/last-commit/Trojan3877/AutoGuard-AI-Real-Time-Autonomous-Vehicle-Safety-Geofencing-Platform)

<img alt="AutoGuard AI architecture diagram" src="https://github.com/user-attachments/assets/23e100bf-9086-4e91-90db-6886e34ec1d6" />

---

## What is AutoGuard AI?

AutoGuard AI ingests real-time telemetry from autonomous vehicle sensor fleets, runs perception and fatigue-detection AI models, enforces geofencing policies, and exposes safety decisions over REST and gRPC. A live Streamlit dashboard streams alerts and metrics to operators.

---

## Repository layout

```
apps/           – frontend (Streamlit dashboard + WebSocket server)
services/       – backend (FastAPI REST + gRPC API)
libs/           – shared libraries
  geofence/         haversine + dynamic geofence radius
  perception/       CNN / ViT obstacle-detection models
  risk-engine-cpp/  C++ latency-critical risk calculator
  models/           fatigue CNN / LSTM, EAR metric, model registry
  streaming/        Kafka producer & consumer
  pipelines/        drift detection, Snowflake loader
  simulation/       Gymnasium RL environments + PPO training
  monitoring/       Prometheus metrics, OpenTelemetry tracing
infra/          – infrastructure-as-code
  k8s/              Kubernetes manifests (HPA)
  helm/             Helm chart
  terraform/        AWS ECR + EKS provisioning
  monitoring/       Grafana dashboard + Prometheus alerts
docs/           – architecture, development guide, structure map
scripts/        – developer utilities (data generation)
tests/          – unit tests, benchmarks and load tests
```

See [`docs/structure.md`](docs/structure.md) for the full annotated tree.

---

## Quick start (local development)

**Prerequisites:** Python 3.10+, Docker + Compose.

```bash
# Clone
git clone https://github.com/Trojan3877/AutoGuard-AI-Real-Time-Autonomous-Vehicle-Safety-Geofencing-Platform.git
cd AutoGuard-AI-Real-Time-Autonomous-Vehicle-Safety-Geofencing-Platform

# Copy and fill in environment variables
cp .env.example .env
# Edit .env with your credentials (GOOGLE_API_KEY, Snowflake, etc.)

# Install dependencies
python3 -m venv .venv && source .venv/bin/activate
make install

# Start Kafka + Redis
make infra-up

# Start the FastAPI backend  →  http://localhost:8000
make dev-api

# Start the gRPC server  →  :50051  (separate terminal)
make dev-grpc

# Start the Streamlit dashboard  →  http://localhost:8501  (separate terminal)
make dev-dashboard
```

For a complete guide (env vars, RL training, Docker build, K8s deploy) see [`docs/development.md`](docs/development.md).

---

## Docker Compose (full stack)

```bash
cp .env.example .env   # fill in your secrets
docker compose up --build
```

Services:
| Service | URL |
|---|---|
| FastAPI REST | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| Streamlit dashboard | http://localhost:8501 |
| gRPC | localhost:50051 |

---

## Architecture flow

```
Sensor Fleet  →  Kafka  →  Perception AI  +  Fatigue AI
                                   ↓
                           C++ Risk Engine
                                   ↓
                    FastAPI / gRPC  ←→  Redis Cache
                           ↓             ↓
                    A/B Routing    Load Balancer
                           ↓
                    Streamlit Dashboard (WebSocket)
                           ↓
              Prometheus Metrics + OpenTelemetry Traces
                           ↓
                  Kubernetes HPA (auto-scaling)
```

---

## Components

| Path | Description |
|---|---|
| `services/api/` | FastAPI REST API + gRPC inference server, Redis caching, A/B routing |
| `apps/dashboard/` | Streamlit control-centre + WebSocket telemetry feed |
| `libs/perception/` | CNN and Vision-Transformer obstacle-detection models (CUDA-ready) |
| `libs/models/` | Fatigue CNN/LSTM, Eye-Aspect-Ratio metric, model registry |
| `libs/geofence/` | Haversine distance + dynamic geofence radius |
| `libs/risk-engine-cpp/` | Low-latency C++ risk-score calculation |
| `libs/streaming/` | Apache Kafka producer and consumer |
| `libs/pipelines/` | KS-test drift detection, Snowflake data loader |
| `libs/simulation/` | Gymnasium RL environments + Stable-Baselines3 PPO training |
| `libs/monitoring/` | Prometheus counters/histograms, OpenTelemetry tracing |
| `infra/terraform/` | AWS ECR + EKS cluster provisioning |
| `infra/k8s/` | Kubernetes manifests + HPA |
| `infra/helm/` | Helm chart for production deployments |

---

## Environment variables

Copy `.env.example` to `.env` and fill in real values before running locally.

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google Maps API key for geofencing |
| `REDIS_HOST` / `REDIS_PORT` | Redis connection |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker address(es) |
| `SNOWFLAKE_*` | Snowflake data-pipeline credentials |
| `API_BASE_URL` | Base URL the dashboard uses to reach the API (default: `http://localhost:8000`) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OpenTelemetry collector endpoint |

---

## Metrics

| Metric | Value |
|---|---|
| Avg REST latency | 72 ms |
| Avg gRPC latency | 38 ms |
| Redis cache hit rate | 64 % |
| Max load (Locust) | 1 200 RPS |
| HPA scale time | < 15 s |
| Drift sensitivity | 0.92 |
| Collision reduction | 27 % |

---

## Running tests

```bash
make test      # pytest tests/
make coverage  # with coverage report
```

CI uses `requirements-ci.txt` (lightweight, no heavy GPU packages) so tests run quickly on standard runners.

---

## Deployment

```bash
# Build Docker images
docker build -f services/api/Dockerfile -t autoguard-api .
docker build -f apps/dashboard/Dockerfile -t autoguard-dashboard .

# Apply Kubernetes manifests
kubectl apply -f infra/k8s/

# Helm deploy
helm upgrade --install autoguard ./infra/helm/autoguard \
  --namespace autoguard --create-namespace
```

For the full Kubernetes + Terraform workflow see [`docs/development.md`](docs/development.md).

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for branching strategy, commit conventions, and code style.

## License

MIT – see [`LICENSE`](LICENSE).
