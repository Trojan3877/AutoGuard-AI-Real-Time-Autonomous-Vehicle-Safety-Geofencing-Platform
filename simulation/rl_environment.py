import gym
import numpy as np

class AutoGuardEnv(gym.Env):
    def __init__(self):
        super(AutoGuardEnv, self).__init__()
        self.state = np.zeros(4)
        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(4,))

    def step(self, action):
        reward = 1.0
        done = False

        if action == 2:  # Simulate collision
            reward = -10
            done = True

        self.state = np.random.uniform(-1, 1, size=(4,))
        return self.state, reward, done, {}

    def reset(self):
        self.state = np.zeros(4)
        return self.state
