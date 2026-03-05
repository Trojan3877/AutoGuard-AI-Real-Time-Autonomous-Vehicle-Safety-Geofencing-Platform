import pandas as pd
import numpy as np

def generate_dataset(size=10000):
    data = {
        "speed": np.random.uniform(0, 120, size),
        "latitude": 37.77 + np.random.uniform(-0.02, 0.02, size),
        "longitude": -122.41 + np.random.uniform(-0.02, 0.02, size),
        "eye_aspect_ratio": np.random.uniform(0.15, 0.35, size),
        "collision_risk": np.random.randint(0, 2, size)
    }
    df = pd.DataFrame(data)
    df.to_csv("synthetic_vehicle_data.csv", index=False)
    print("Dataset generated.")

if __name__ == "__main__":
    generate_dataset()
