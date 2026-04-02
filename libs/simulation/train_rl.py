from stable_baselines3 import PPO
from .driving_env import DrivingEnv

env = DrivingEnv()
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)
model.save("rl_driver_policy")
