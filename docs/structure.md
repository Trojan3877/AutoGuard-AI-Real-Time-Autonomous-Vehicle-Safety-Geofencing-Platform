# Repository Structure

```
AutoGuard-AI/
│
├── apps/
│   └── dashboard/
│       ├── streamlit_app.py      # Streamlit control-centre UI
│       └── ws_server.py          # WebSocket telemetry push server
│
├── services/
│   └── api/
│       ├── main.py               # FastAPI REST entry-point
│       ├── geofence.py           # Geofence validation (Google Maps)
│       ├── grpc_server.py        # gRPC inference service
│       ├── inference.proto       # Protobuf schema
│       ├── ab_testing.py         # A/B model-routing logic
│       ├── load_balancer.py      # Randomised load-balancer helper
│       ├── redis_cache.py        # Redis caching utilities
│       └── Dockerfile            # GPU-ready Docker image
│
├── libs/
│   ├── geofence/
│   │   └── google_maps_geofence.py  # Haversine + dynamic radius
│   ├── perception/
│   │   ├── cuda_utils.py            # CUDA device helpers
│   │   ├── pytorch_model.py         # CNN perception model
│   │   └── transformer_model.py     # ViT perception model
│   ├── risk-engine-cpp/
│   │   └── risk_engine.cpp          # C++ risk-score calculator
│   ├── models/
│   │   ├── ear_metric.py            # Eye Aspect Ratio computation
│   │   ├── fatigue_cnn.py           # CNN fatigue classifier
│   │   ├── fatigue_lstm.py          # LSTM fatigue classifier
│   │   ├── model_registry.py        # Version-based model registry
│   │   └── transformer_perception.py # Custom patch-embed transformer
│   ├── streaming/
│   │   ├── kafka_consumer.py        # Kafka telemetry consumer
│   │   └── kafka_producer.py        # Synthetic sensor producer
│   ├── pipelines/
│   │   ├── drift_detection.py       # KS-test drift detector
│   │   └── snowflake_loader.py      # Snowflake data loader
│   ├── simulation/
│   │   ├── autoguard_env.py         # AutoGuard Gym environment
│   │   ├── driving_env.py           # Generic driving Gym environment
│   │   └── train_rl.py              # PPO training script
│   └── monitoring/
│       ├── prometheus_metrics.py    # Prometheus counters/histograms
│       └── tracing.py               # OpenTelemetry tracing setup
│
├── infra/
│   ├── k8s/
│   │   └── hpa.yaml                 # Horizontal Pod Autoscaler
│   └── terraform/
│       └── main.tf                  # AWS ECR + EKS provisioning
│
├── docs/
│   ├── architecture.md              # System design & data-flow
│   ├── development.md               # Local dev & onboarding guide
│   └── structure.md                 # This file
│
├── scripts/
│   └── generate_data.py             # Synthetic vehicle dataset generator
│
├── tests/
│   ├── benchmarks/
│   │   └── inference_benchmark.py   # REST latency benchmark
│   └── load/
│       └── locustfile.py            # Locust load-test scenario
│
├── .github/
│   └── workflows/
│       ├── ci.yml                   # Pytest + coverage
│       ├── deploy.yml               # Helm deploy to K8s
│       ├── docker-publish.yml       # DockerHub image publish
│       ├── release.yml              # GitHub release notes
│       ├── sbom.yml                 # SBOM generation
│       ├── sonar.yml                # SonarCloud analysis
│       └── trivy.yml                # Container security scan
│
├── docker-compose.yml               # Local Kafka + Redis + API stack
├── Makefile                         # Developer convenience targets
├── requirements.txt                 # Python dependencies
├── .gitignore
├── .editorconfig
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```
