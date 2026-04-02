.PHONY: help install dev-api dev-dashboard dev-grpc test coverage lint format clean

PYTHON ?= python3
PYTHONPATH ?= .

help:            ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install:         ## Install Python dependencies
	pip install -r requirements.txt

dev-api:         ## Start the FastAPI backend (hot-reload)
	PYTHONPATH=$(PYTHONPATH) uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000

dev-grpc:        ## Start the gRPC inference server
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) services/api/grpc_server.py

dev-dashboard:   ## Start the Streamlit dashboard
	PYTHONPATH=$(PYTHONPATH) streamlit run apps/dashboard/streamlit_app.py

dev-ws:          ## Start the WebSocket telemetry server
	PYTHONPATH=$(PYTHONPATH) uvicorn apps.dashboard.ws_server:app --host 0.0.0.0 --port 8080

infra-up:        ## Start Kafka + Redis via docker-compose
	docker-compose up -d kafka redis

infra-down:      ## Stop all docker-compose services
	docker-compose down

test:            ## Run the test suite
	PYTHONPATH=$(PYTHONPATH) pytest tests/ -v

coverage:        ## Run tests with coverage report
	PYTHONPATH=$(PYTHONPATH) coverage run -m pytest tests/ && coverage report

lint:            ## Lint Python code with flake8
	flake8 apps/ services/ libs/ scripts/ tests/ --max-line-length=120

format:          ## Format Python code with black
	black apps/ services/ libs/ scripts/ tests/

generate-data:   ## Generate synthetic vehicle dataset
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) scripts/generate_data.py

train-rl:        ## Train the RL driving policy
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m libs.simulation.train_rl

clean:           ## Remove build / cache artefacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/
