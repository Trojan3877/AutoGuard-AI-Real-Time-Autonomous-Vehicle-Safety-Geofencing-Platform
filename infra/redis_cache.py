import redis
import json
import hashlib

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def cache_key(payload):
    return hashlib.sha256(json.dumps(payload).encode()).hexdigest()

def get_cached(payload):
    key = cache_key(payload)
    result = redis_client.get(key)
    return json.loads(result) if result else None

def set_cache(payload, response):
    key = cache_key(payload)
    redis_client.setex(key, 60, json.dumps(response))  # TTL 60 sec
