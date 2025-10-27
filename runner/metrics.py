import numpy as np
from typing import List, Dict, Any


class Metrics:
    """
    Utility class for computing TSP evaluation metrics.
    """
    
    @staticmethod
    def total_distance(route: List[int], distance_matrix: np.ndarray) -> float:
        """
        Calculate total distance of a route.
        
        Args:
            route: List of location indices in visit order
            distance_matrix: NxN distance matrix
            
        Returns:
            Total distance in kilometers
        """
        if len(route) <= 1:
            return 0.0
        
        total = 0.0
        for i in range(len(route) - 1):
            total += distance_matrix[route[i]][route[i+1]]
        
        return total
    
    @staticmethod
    def route_efficiency(route: List[int], distance_matrix: np.ndarray) -> float:
        """
        Calculate route efficiency as ratio of optimal to actual distance.
        Lower values indicate better efficiency.
        
        Args:
            route: List of location indices in visit order
            distance_matrix: NxN distance matrix
            
        Returns:
            Efficiency ratio (actual_distance / optimal_distance)
        """
        actual_distance = Metrics.total_distance(route, distance_matrix)
        
        # Estimate optimal distance using nearest neighbor as baseline
        # This is a rough approximation
        n = len(distance_matrix)
        if n <= 1:
            return 1.0
        
        # Simple lower bound: sum of minimum distances from each node
        min_distances = [min(row[i] for i in range(n) if i != j) 
                        for j, row in enumerate(distance_matrix)]
        estimated_optimal = sum(min_distances)
        
        if estimated_optimal == 0:
            return 1.0
        
        return actual_distance / estimated_optimal
    
    @staticmethod
    def compare_routes(routes: List[List[int]], distance_matrix: np.ndarray) -> Dict[str, Any]:
        """
        Compare multiple routes and return statistics.
        
        Args:
            routes: List of routes to compare
            distance_matrix: NxN distance matrix
            
        Returns:
            Dictionary with comparison statistics
        """
        distances = [Metrics.total_distance(route, distance_matrix) for route in routes]
        
        return {
            "distances": distances,
            "best_distance": min(distances),
            "worst_distance": max(distances),
            "average_distance": np.mean(distances),
            "std_distance": np.std(distances),
            "improvement_over_worst": (max(distances) - min(distances)) / max(distances) * 100
        }
