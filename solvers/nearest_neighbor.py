import time
import numpy as np
from typing import List, Dict, Any, Tuple
from .base_solver import BaseSolver


class NearestNeighborSolver(BaseSolver):
    """
    Greedy Nearest Neighbor heuristic for TSP.
    
    Algorithm:
    1. Start at the depot (first location)
    2. Repeatedly visit the nearest unvisited location
    3. Return to depot after visiting all locations
    
    Time Complexity: O(n²)
    Space Complexity: O(n)
    """
    
    def __init__(self):
        super().__init__("Nearest Neighbor")
    
    def solve(self, distance_matrix: np.ndarray, locations: List[Dict[str, Any]]) -> Tuple[List[int], float]:
        """
        Solve TSP using nearest neighbor heuristic.
        
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
        
        # Start at depot (index 0)
        route = [0]
        unvisited = set(range(1, n))
        current = 0
        
        # Greedily select nearest unvisited location
        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        # Return to depot
        route.append(0)
        
        # Calculate total distance
        total_distance = sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
        
        self.solve_time = time.time() - start_time
        
        return route, total_distance
