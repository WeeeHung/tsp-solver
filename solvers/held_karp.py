import time
import numpy as np
from typing import List, Dict, Any, Tuple
from .base_solver import BaseSolver


class HeldKarpSolver(BaseSolver):
    """
    Held-Karp Dynamic Programming algorithm for TSP.
    
    This is an exact algorithm that finds the optimal TSP solution using dynamic programming.
    
    Algorithm:
    1. Use bitmask DP to track visited locations
    2. dp[mask][i] = minimum distance to visit all locations in 'mask' and end at location i
    3. Build the solution by backtracking through the DP table
    
    Time Complexity: O(n² * 2^n)
    Space Complexity: O(n * 2^n)
    
    Note: This algorithm is exact but only practical for small instances (n ≤ 20)
    due to exponential complexity.
    """
    
    def __init__(self):
        super().__init__("Held-Karp (DP)")
    
    def solve(self, distance_matrix: np.ndarray, locations: List[Dict[str, Any]]) -> Tuple[List[int], float]:
        """
        Solve TSP using Held-Karp dynamic programming.
        
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
        
        # For large instances, warn about computational cost
        if n > 20:
            print(f"⚠️  Warning: Held-Karp may be slow for {n} locations (2^{n} = {2**n:,} subproblems)")
        
        # DP table: dp[mask][i] = (min_distance, previous_location)
        # mask represents the set of visited locations
        # i is the current ending location
        dp = {}
        
        # Base case: starting from location 0 with only location 0 visited
        start_mask = 1 << 0  # Binary: 0001 (only bit 0 set)
        for i in range(1, n):
            mask = start_mask | (1 << i)  # Visit location 0 and i
            dp[(mask, i)] = (distance_matrix[0][i], 0)
        
        # Fill DP table for increasingly larger subsets
        for subset_size in range(3, n + 1):
            # Generate all subsets of size subset_size that include location 0
            for mask in range(1 << n):
                # Skip if location 0 is not in the mask
                if not (mask & (1 << 0)):
                    continue
                
                # Skip if the number of set bits != subset_size
                if bin(mask).count('1') != subset_size:
                    continue
                
                # Try ending at each location in the mask (except 0)
                for curr in range(1, n):
                    if not (mask & (1 << curr)):
                        continue
                    
                    # Try all possible previous locations
                    prev_mask = mask ^ (1 << curr)  # Remove curr from mask
                    
                    min_dist = float('inf')
                    best_prev = -1
                    
                    for prev in range(1, n):
                        if not (prev_mask & (1 << prev)):
                            continue
                        
                        if (prev_mask, prev) in dp:
                            dist = dp[(prev_mask, prev)][0] + distance_matrix[prev][curr]
                            if dist < min_dist:
                                min_dist = dist
                                best_prev = prev
                    
                    if best_prev != -1:
                        dp[(mask, curr)] = (min_dist, best_prev)
        
        # Find the best complete tour (all locations visited)
        full_mask = (1 << n) - 1  # All bits set
        min_tour_dist = float('inf')
        best_last = -1
        
        for last in range(1, n):
            if (full_mask, last) in dp:
                # Add distance to return to start
                tour_dist = dp[(full_mask, last)][0] + distance_matrix[last][0]
                if tour_dist < min_tour_dist:
                    min_tour_dist = tour_dist
                    best_last = last
        
        # Reconstruct the route by backtracking
        route = []
        mask = full_mask
        curr = best_last
        
        while curr != 0:
            route.append(curr)
            prev = dp[(mask, curr)][1]
            mask = mask ^ (1 << curr)
            curr = prev
        
        route.append(0)
        route.reverse()
        route.append(0)  # Return to start
        
        self.solve_time = time.time() - start_time
        
        return route, min_tour_dist

