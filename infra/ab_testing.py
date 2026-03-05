import random

def select_model():
    if random.random() < 0.8:
        return "model_v1"
    return "model_v2"
