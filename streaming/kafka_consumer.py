from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "vehicle_telemetry",
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    telemetry = message.value
    print("Received:", telemetry)
