import time
import numpy as np
from typing import List, Dict, Any, Tuple

from .base_solver import BaseSolver
from train.model import generate_route

class RLSolver(BaseSolver):
    """
    Reinforcement Learning based solver for TSP.
    
    This solver uses a pre-trained RL model to predict the route for TSP.
    
    Time Complexity: O(n^3)
    Space Complexity: O(n^2)
    """
    
    def __init__(self):
        super().__init__("RL Solver")
    
    def solve(self, distance_matrix: np.ndarray, locations: List[Dict[str, Any]]) -> Tuple[List[int], float]:
        """
        Solve TSP using the RL model.
        
        Args:
            distance_matrix: NxN matrix of distances between locations
            locations: List of location dictionaries
            
        Returns:
            Tuple of (route, total_distance)
        """
        start_time = time.time()
        
        n = len(locations)
        if n <= 1:
            return [0], 0.0
        
        # Get predicted route from the RL model
        route = generate_route(distance_matrix)
        
        # Return to depot
        route.append(route[0])
        
        # Calculate total distance
        total_distance = sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
        
        self.solve_time = time.time() - start_time

        return route, total_distance
