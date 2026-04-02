import gym
from gym import spaces
import numpy as np

class DrivingEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(3)  # left, right, forward
        self.observation_space = spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32)

    def step(self, action):
        reward = np.random.rand()
        done = reward > 0.95
        return np.random.rand(5), reward, done, {}

    def reset(self):
        return np.random.rand(5)
