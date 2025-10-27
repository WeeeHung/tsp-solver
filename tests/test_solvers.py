import unittest
import numpy as np
from solvers.nearest_neighbor import NearestNeighborSolver
from solvers.ortools_solver import ORToolsSolver


class TestSolvers(unittest.TestCase):
    """Unit tests for TSP solvers."""
    
    def setUp(self):
        """Set up test data."""
        # Simple 4-city TSP instance
        self.distance_matrix = np.array([
            [0, 10, 15, 20],
            [10, 0, 35, 25],
            [15, 35, 0, 30],
            [20, 25, 30, 0]
        ])
        
        self.locations = [
            {"id": 0, "name": "City A", "lat": 0, "lon": 0},
            {"id": 1, "name": "City B", "lat": 0, "lon": 10},
            {"id": 2, "name": "City C", "lat": 10, "lon": 10},
            {"id": 3, "name": "City D", "lat": 10, "lon": 0}
        ]
    
    def test_nearest_neighbor_solver(self):
        """Test Nearest Neighbor solver."""
        solver = NearestNeighborSolver()
        route, distance = solver.solve(self.distance_matrix, self.locations)
        
        # Check route format
        self.assertEqual(len(route), len(self.locations) + 1)  # Includes return to depot
        self.assertEqual(route[0], 0)  # Starts at depot
        self.assertEqual(route[-1], 0)  # Returns to depot
        
        # Check distance is positive
        self.assertGreater(distance, 0)
        
        # Check solve time is recorded
        self.assertGreater(solver.get_solve_time(), 0)
    
    def test_ortools_solver(self):
        """Test OR-Tools solver."""
        solver = ORToolsSolver("first_solution")
        route, distance = solver.solve(self.distance_matrix, self.locations)
        
        # Check route format
        self.assertEqual(len(route), len(self.locations) + 1)  # Includes return to depot
        self.assertEqual(route[0], 0)  # Starts at depot
        self.assertEqual(route[-1], 0)  # Returns to depot
        
        # Check distance is positive
        self.assertGreater(distance, 0)
        
        # Check solve time is recorded
        self.assertGreater(solver.get_solve_time(), 0)
    
    def test_solver_comparison(self):
        """Test that both solvers can solve the same instance."""
        nn_solver = NearestNeighborSolver()
        ortools_solver = ORToolsSolver("first_solution")
        
        nn_route, nn_distance = nn_solver.solve(self.distance_matrix, self.locations)
        ortools_route, ortools_distance = ortools_solver.solve(self.distance_matrix, self.locations)
        
        # Both should return valid routes
        self.assertGreater(nn_distance, 0)
        self.assertGreater(ortools_distance, 0)
        
        # OR-Tools should generally find better solutions than Nearest Neighbor
        # (though this isn't guaranteed for all instances)
        print(f"Nearest Neighbor: {nn_distance:.2f}")
        print(f"OR-Tools: {ortools_distance:.2f}")
    
    def test_empty_instance(self):
        """Test solvers with empty instance."""
        empty_matrix = np.array([[0]])
        empty_locations = [{"id": 0, "name": "Depot", "lat": 0, "lon": 0}]
        
        nn_solver = NearestNeighborSolver()
        route, distance = nn_solver.solve(empty_matrix, empty_locations)
        
        self.assertEqual(route, [0])
        self.assertEqual(distance, 0.0)


if __name__ == '__main__':
    unittest.main()
