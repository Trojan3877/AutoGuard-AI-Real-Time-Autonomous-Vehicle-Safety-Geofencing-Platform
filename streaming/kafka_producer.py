from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def simulate_sensor_stream():
    while True:
        data = {
            "speed": random.uniform(0, 120),
            "latitude": 37.7749 + random.uniform(-0.01, 0.01),
            "longitude": -122.4194 + random.uniform(-0.01, 0.01),
            "eye_aspect_ratio": random.uniform(0.15, 0.35)
        }
        producer.send("vehicle_telemetry", data)
        time.sleep(1)

if __name__ == "__main__":
    simulate_sensor_stream()
