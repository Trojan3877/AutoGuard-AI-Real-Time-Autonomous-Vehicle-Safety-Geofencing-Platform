from prometheus_client import Counter, Histogram

request_counter = Counter("api_requests_total", "Total API Requests")
inference_latency = Histogram("inference_latency_seconds", "Inference Latency")
