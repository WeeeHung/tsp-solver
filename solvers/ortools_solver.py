import time
import numpy as np
from typing import List, Dict, Any, Tuple
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from .base_solver import BaseSolver


class ORToolsSolver(BaseSolver):
    """
    Google OR-Tools based TSP solver using the routing library.
    
    Uses metaheuristics and local search to find near-optimal solutions.
    More sophisticated than greedy heuristics but still heuristic-based.
    """
    
    def __init__(self, search_strategy: str = "first_solution"):
        """
        Initialize OR-Tools solver.
        
        Args:
            search_strategy: Strategy for finding solutions
                - "first_solution": Find first feasible solution quickly
                - "local_search": Use local search for better solutions
        """
        super().__init__(f"OR-Tools ({search_strategy})")
        self.search_strategy = search_strategy
    
    def solve(self, distance_matrix: np.ndarray, locations: List[Dict[str, Any]]) -> Tuple[List[int], float]:
        """
        Solve TSP using OR-Tools routing library.
        
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
        
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(n, 1, 0)  # 1 vehicle, depot at 0
        routing = pywrapcp.RoutingModel(manager)
        
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node] * 1000)  # Convert to integer
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        
        if self.search_strategy == "first_solution":
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
        elif self.search_strategy == "local_search":
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            )
            search_parameters.time_limit.seconds = 30  # 30 second time limit
        
        # Solve the problem
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution is None:
            # Fallback to nearest neighbor if OR-Tools fails
            from .nearest_neighbor import NearestNeighborSolver
            nn_solver = NearestNeighborSolver()
            return nn_solver.solve(distance_matrix, locations)
        
        # Extract route
        route = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))  # Add depot at end
        
        # Calculate total distance
        total_distance = sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
        
        self.solve_time = time.time() - start_time
        
        return route, total_distance
