from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
import numpy as np


class BaseSolver(ABC):
    """
    Abstract base class for TSP solvers.
    All solvers must implement the solve method.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.solve_time = 0.0
    
    @abstractmethod
    def solve(self, distance_matrix: np.ndarray, locations: List[Dict[str, Any]]) -> Tuple[List[int], float]:
        """
        Solve the TSP instance.
        
        Args:
            distance_matrix: NxN matrix of distances between locations
            locations: List of location dictionaries with 'id', 'name', 'lat', 'lon'
            
        Returns:
            Tuple of (route, total_distance)
            - route: List of location indices in visit order
            - total_distance: Total distance of the route
        """
        pass
    
    def get_solve_time(self) -> float:
        """Get the time taken to solve the last instance."""
        return self.solve_time
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
