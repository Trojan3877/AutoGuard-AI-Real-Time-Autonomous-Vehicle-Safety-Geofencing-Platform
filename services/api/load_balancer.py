import requests
import random

INFERENCE_SERVERS = [
    "http://localhost:8001/predict",
    "http://localhost:8002/predict",
    "http://localhost:8003/predict"
]

def route_request(payload):
    server = random.choice(INFERENCE_SERVERS)
    response = requests.post(server, json=payload)
    return response.json()
