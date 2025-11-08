from typing import Optional
import numpy as np
import random
import gymnasium as gym
import matplotlib.pyplot as plt
from scipy.spatial import distance_matrix

from utils import total_distance

class TSPEnv(gym.Env):
    def __init__(self, num_cities: int = 10):
        super(TSPEnv, self).__init__()
        self.num_cities = num_cities
        self.cities = None
        self.W = None
        self.normalized_W = None
        self.partial_solution = []

        self.action_space = gym.spaces.Discrete(num_cities)
        self.observation_space = gym.spaces.Dict(
            {
                "W": gym.spaces.Box(low=0, high=np.inf, shape=(num_cities, num_cities), dtype=np.float32),
                "coords": gym.spaces.Box(low=0, high=1, shape=(num_cities, 2), dtype=np.float32),
                "partial_solution": gym.spaces.Sequence(gym.spaces.Discrete(num_cities))
            }
        )

    def _generate_cities(self):
        """Generate random cities in a 2D space."""
        self.cities = self.np_random.uniform(0, 1, (self.num_cities, 2))
        self.W = distance_matrix(self.cities, self.cities)
        self.normalized_W = self.W / np.max(self.W) if np.max(self.W) > 0 else self.W

    def plot_graph(self):
        """ Utility function to plot the fully connected graph
        """
        n = len(self.cities)

        plt.scatter(self.cities[:,0], self.cities[:,1], s=[50 for _ in range(n)])
        for i in range(n):
            for j in range(n):
                if j < i:
                    plt.plot([self.cities[i,0], self.cities[j,0]], [self.cities[i,1], self.cities[j,1]], 'b', alpha=0.7)

    def is_terminated(self):
        """Check if the current episode is terminated.

        Returns:
            bool: True if the episode is terminated, False otherwise.
        """
        return len(self.partial_solution) >= self.num_cities
    
    def sample_random_action(self):
        """Sample a random valid action.

        Returns:
            int: The index of the next city to visit.
        """
        available_actions = list(set(range(self.num_cities)) - set(self.partial_solution))
        return random.choice(available_actions)
    
    def _get_obs(self):
        """Convert internal state to observation format.
        
        Returns:
            observation: dict: The current observation
        """
        return {
            "W": self.W.astype(np.float32),
            "coords": self.cities.astype(np.float32),
            "partial_solution": self.partial_solution.copy()
        }

    def _compute_reward(self, next_solution):
        """Compute the reward for the current partial solution.

        Returns:
            float: The computed reward.
        """
        reward = -(total_distance(next_solution, self.normalized_W) - total_distance(self.partial_solution, self.normalized_W))
        return reward

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        """Start a new episode.

        Args:
            seed: Random seed for reproducible episodes
            options: Additional configuration (unused in this example)

        Returns:
            tuple: (observation, info) for the initial state
        """
        super().reset(seed=seed)
        
        self._generate_cities()
        self.partial_solution = []
        observation = self._get_obs()
        info = {}
        return observation, info

    def step(self, action):
        """Execute one timestep within the environment.

        Args:
            action: The index of the next city to visit.

        Returns:
            tuple: (observation, reward, terminated, truncated, info)
        """

        # Placeholder implementation for step function
        next_solution = self.partial_solution + [action]
        reward = self._compute_reward(next_solution)
        self.partial_solution = next_solution
        observation = self._get_obs()
        terminated = self.is_terminated()
        truncated = False
        info = {}

        return observation, reward, terminated, truncated, info

    def render(self):
        pass  # Rendering logic can be implemented here if needed


if __name__ == "__main__":
    env = TSPEnv(num_cities=5)
    obs, info = env.reset(seed=42)
    print("Initial Observation:\n", obs)
    print(env.observation_space.sample())
    env.plot_graph()
    plt.show()