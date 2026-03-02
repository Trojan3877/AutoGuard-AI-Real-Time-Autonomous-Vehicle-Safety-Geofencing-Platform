from prometheus_client import Counter

request_counter = Counter("api_requests_total", "Total API Requests")
