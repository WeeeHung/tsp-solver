import time
import numpy as np
from typing import List, Dict, Any, Tuple, Set
from .base_solver import BaseSolver


class BranchAndBoundSolver(BaseSolver):
    """
    Branch and Bound algorithm for TSP.
    
    This is an exact algorithm that uses tree search with pruning to find
    the optimal TSP solution.
    
    Algorithm:
    1. Start with a greedy solution as the upper bound
    2. Use DFS to explore partial tours
    3. Prune branches when the lower bound exceeds the current best solution
    4. Lower bound is calculated using the minimum spanning tree (MST) heuristic
    
    Time Complexity: O(n!) worst case, but much better in practice with pruning
    Space Complexity: O(n) for recursion stack
    
    Note: This algorithm is exact but may be slow for large instances (n > 20)
    without good pruning.
    """
    
    def __init__(self):
        super().__init__("Branch & Bound")
        self.best_distance = float('inf')
        self.best_route = []
        self.nodes_explored = 0
        self.nodes_pruned = 0
    
    def solve(self, distance_matrix: np.ndarray, locations: List[Dict[str, Any]]) -> Tuple[List[int], float]:
        """
        Solve TSP using Branch and Bound.
        
        Args:
            distance_matrix: NxN matrix of distances between locations
            locations: List of location dictionaries
            
        Returns:
            Tuple of (route, total_distance)
        """
        start_time = time.time()
        
        n = len(locations)
        
        # Handle edge cases
        if n <= 1:
            return [0], 0.0
        
        if n == 2:
            route = [0, 1, 0]
            total_distance = distance_matrix[0][1] + distance_matrix[1][0]
            self.solve_time = time.time() - start_time
            return route, total_distance
        
        # Initialize
        self.best_distance = float('inf')
        self.best_route = []
        self.nodes_explored = 0
        self.nodes_pruned = 0
        
        # Get initial upper bound using greedy nearest neighbor
        initial_route, initial_distance = self._greedy_solution(distance_matrix, n)
        self.best_distance = initial_distance
        self.best_route = initial_route.copy()
        
        # Start branch and bound from location 0
        current_route = [0]
        visited = {0}
        current_distance = 0.0
        
        self._branch_and_bound(
            distance_matrix,
            n,
            current_route,
            visited,
            current_distance
        )
        
        self.solve_time = time.time() - start_time
        
        # Print statistics
        print(f"    Nodes explored: {self.nodes_explored:,}, Nodes pruned: {self.nodes_pruned:,}")
        
        return self.best_route, self.best_distance
    
    def _greedy_solution(self, distance_matrix: np.ndarray, n: int) -> Tuple[List[int], float]:
        """
        Get initial solution using greedy nearest neighbor heuristic.
        
        Args:
            distance_matrix: Distance matrix
            n: Number of locations
            
        Returns:
            Tuple of (route, distance)
        """
        route = [0]
        visited = {0}
        current = 0
        
        while len(visited) < n:
            nearest = min(
                (i for i in range(n) if i not in visited),
                key=lambda x: distance_matrix[current][x]
            )
            route.append(nearest)
            visited.add(nearest)
            current = nearest
        
        route.append(0)
        
        # Calculate total distance
        total_distance = sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
        
        return route, total_distance
    
    def _calculate_lower_bound(
        self,
        distance_matrix: np.ndarray,
        n: int,
        current_route: List[int],
        visited: Set[int],
        current_distance: float
    ) -> float:
        """
        Calculate lower bound for the current partial tour using MST heuristic.
        
        Lower bound = current_distance + MST of unvisited nodes + 
                     min edge from last node to unvisited + 
                     min edge from unvisited to start
        
        Args:
            distance_matrix: Distance matrix
            n: Number of locations
            current_route: Current partial route
            visited: Set of visited locations
            current_distance: Distance traveled so far
            
        Returns:
            Lower bound estimate
        """
        if len(visited) == n:
            # Complete tour - just add return distance
            return current_distance + distance_matrix[current_route[-1]][0]
        
        # Get unvisited nodes
        unvisited = [i for i in range(n) if i not in visited]
        
        if not unvisited:
            return current_distance + distance_matrix[current_route[-1]][0]
        
        # Start with current distance
        lower_bound = current_distance
        
        # Add minimum edge from last visited node to any unvisited node
        last_node = current_route[-1]
        min_to_unvisited = min(distance_matrix[last_node][node] for node in unvisited)
        lower_bound += min_to_unvisited
        
        # Add minimum edge from any unvisited node back to start (node 0)
        min_to_start = min(distance_matrix[node][0] for node in unvisited)
        lower_bound += min_to_start
        
        # Add MST cost of unvisited nodes (simplified - just use minimum edges)
        if len(unvisited) > 1:
            mst_cost = self._simple_mst(distance_matrix, unvisited)
            lower_bound += mst_cost
        
        return lower_bound
    
    def _simple_mst(self, distance_matrix: np.ndarray, nodes: List[int]) -> float:
        """
        Calculate MST cost using Prim's algorithm (simplified).
        
        Args:
            distance_matrix: Distance matrix
            nodes: List of nodes to include in MST
            
        Returns:
            MST cost
        """
        if len(nodes) <= 1:
            return 0.0
        
        # Prim's algorithm
        in_mst = {nodes[0]}
        mst_cost = 0.0
        
        while len(in_mst) < len(nodes):
            # Find minimum edge from MST to outside
            min_edge = float('inf')
            for u in in_mst:
                for v in nodes:
                    if v not in in_mst:
                        if distance_matrix[u][v] < min_edge:
                            min_edge = distance_matrix[u][v]
                            next_node = v
            
            in_mst.add(next_node)
            mst_cost += min_edge
        
        return mst_cost
    
    def _branch_and_bound(
        self,
        distance_matrix: np.ndarray,
        n: int,
        current_route: List[int],
        visited: Set[int],
        current_distance: float
    ) -> None:
        """
        Recursive branch and bound search.
        
        Args:
            distance_matrix: Distance matrix
            n: Number of locations
            current_route: Current partial route
            visited: Set of visited locations
            current_distance: Distance traveled so far
        """
        self.nodes_explored += 1
        
        # Base case: all locations visited
        if len(visited) == n:
            # Add return to start
            total_distance = current_distance + distance_matrix[current_route[-1]][0]
            
            if total_distance < self.best_distance:
                self.best_distance = total_distance
                self.best_route = current_route + [0]
            
            return
        
        # Calculate lower bound
        lower_bound = self._calculate_lower_bound(
            distance_matrix, n, current_route, visited, current_distance
        )
        
        # Prune if lower bound exceeds best known solution
        if lower_bound >= self.best_distance:
            self.nodes_pruned += 1
            return
        
        # Branch: try each unvisited location
        current_node = current_route[-1]
        
        # Sort unvisited nodes by distance (best-first search for better pruning)
        unvisited = [(i, distance_matrix[current_node][i]) 
                    for i in range(n) if i not in visited]
        unvisited.sort(key=lambda x: x[1])
        
        for next_node, edge_dist in unvisited:
            # Add next node to route
            new_route = current_route + [next_node]
            new_visited = visited | {next_node}
            new_distance = current_distance + edge_dist
            
            # Recurse
            self._branch_and_bound(
                distance_matrix,
                n,
                new_route,
                new_visited,
                new_distance
            )

