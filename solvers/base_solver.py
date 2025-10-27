from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
import numpy as np


class BaseSolver(ABC):
    """
    Abstract base class for TSP solvers.
    All solvers must implement the solve method.
    
    To create a new solver, inherit from this class and implement the solve method.
    See the example below for the expected input/output format.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.solve_time = 0.0
    
    @abstractmethod
    def solve(self, distance_matrix: np.ndarray, locations: List[Dict[str, Any]]) -> Tuple[List[int], float]:
        """
        Solve the TSP instance.
        
        Args:
            distance_matrix: NxN matrix of distances between locations (in kilometers)
                Example for 4 locations:
                    [[0.0,  5.2,  8.1,  3.4],
                     [5.2,  0.0,  6.3,  7.1],
                     [8.1,  6.3,  0.0,  4.5],
                     [3.4,  7.1,  4.5,  0.0]]
                Note: distance_matrix[i][j] is the distance from location i to location j
            
            locations: List of location dictionaries with the following structure:
                Example:
                    [
                        {"id": 0, "name": "Marina Bay Sands", "lat": 1.2834, "lon": 103.8607},
                        {"id": 1, "name": "Gardens by the Bay", "lat": 1.2816, "lon": 103.8636},
                        {"id": 2, "name": "Raffles Hotel", "lat": 1.2945, "lon": 103.8545},
                        {"id": 3, "name": "Sentosa Island", "lat": 1.2494, "lon": 103.8303}
                    ]
            
        Returns:
            Tuple of (route, total_distance) where:
            
            route: List of location indices representing the visiting order (must start and end at 0)
                Example: [0, 2, 1, 3, 0]
                This means: Start at location 0 → visit 2 → visit 1 → visit 3 → return to 0
            
            total_distance: Total distance of the route in kilometers (float)
                Example: 23.5
        
        Example Implementation:
            def solve(self, distance_matrix, locations):
                import time
                start_time = time.time()
                
                # Your algorithm here
                n = len(locations)
                route = list(range(n)) + [0]  # Simple route: 0→1→2→...→n-1→0
                
                # Calculate total distance
                total_distance = sum(distance_matrix[route[i]][route[i+1]] 
                                    for i in range(len(route)-1))
                
                self.solve_time = time.time() - start_time
                return route, total_distance
        """
        pass
    
    def get_solve_time(self) -> float:
        """Get the time taken to solve the last instance."""
        return self.solve_time
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
