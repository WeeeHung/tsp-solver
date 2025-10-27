import json
import os
import time
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from geopy.distance import geodesic
from solvers.base_solver import BaseSolver
from solvers.nearest_neighbor import NearestNeighborSolver
from solvers.ortools_solver import ORToolsSolver
from utils.distance_calculator import DistanceCalculator
from utils.geocoder import LocationGeocoder


class SolverRunner:
    """
    Framework to run and compare multiple TSP solvers on test instances.
    """
    
    def __init__(self, data_dir: str = "data", use_google_maps: bool = True):
        self.data_dir = data_dir
        self.locations = []
        self.test_instances = []
        self.results = []
        self.distance_calculator = DistanceCalculator(use_google_maps=use_google_maps)
        self.geocoder = None
    
    def load_locations(self, locations_file: str = "singapore_locations.json") -> None:
        """
        Load locations from JSON file.
        
        Args:
            locations_file: Name of the locations file in data directory
        """
        locations_path = os.path.join(self.data_dir, locations_file)
        with open(locations_path, 'r') as f:
            data = json.load(f)
        self.locations = data["locations"]
        print(f"📍 Loaded {len(self.locations)} locations from {locations_file}")
    
    def load_locations_from_names(self, location_names: List[str], 
                                  region: str = "sg",
                                  save_to_file: Optional[str] = None) -> None:
        """
        Geocode location names and load them as locations.
        
        Args:
            location_names: List of location names or addresses
            region: Region bias for geocoding (default: "sg" for Singapore)
            save_to_file: Optional filename to save geocoded locations
        """
        if self.geocoder is None:
            self.geocoder = LocationGeocoder()
        
        self.locations = self.geocoder.geocode_locations(location_names, region=region)
        
        if save_to_file and self.locations:
            output_path = os.path.join(self.data_dir, save_to_file)
            self.geocoder.save_locations_to_json(self.locations, output_path)
        
        print(f"📍 Loaded {len(self.locations)} geocoded locations")
    
    def load_test_instances(self, locations_file: str = "singapore_locations.json") -> None:
        """
        Load test instances from JSON files.
        
        Args:
            locations_file: Name of the locations file to use
        """
        self.load_locations(locations_file)
        
        instances_dir = os.path.join(self.data_dir, "test_instances")
        for filename in os.listdir(instances_dir):
            if filename.endswith('.json'):
                instance_path = os.path.join(instances_dir, filename)
                with open(instance_path, 'r') as f:
                    instance = json.load(f)
                self.test_instances.append(instance)
        
        print(f"📋 Loaded {len(self.test_instances)} test instances")
    
    def create_custom_instance(self, location_names: List[str], 
                              instance_name: str,
                              region: str = "sg") -> Dict[str, Any]:
        """
        Create a custom TSP instance from location names.
        
        Args:
            location_names: List of location names or addresses
            instance_name: Name for this instance
            region: Region bias for geocoding
            
        Returns:
            Dictionary representing the TSP instance
        """
        # Geocode the locations
        if self.geocoder is None:
            self.geocoder = LocationGeocoder()
        
        locations = self.geocoder.geocode_locations(location_names, region=region)
        
        if not locations:
            raise ValueError("No locations were successfully geocoded")
        
        # Set as current locations if not already set
        if not self.locations:
            self.locations = locations
        else:
            # Merge with existing locations
            self.locations.extend(locations)
        
        # Create instance
        instance = {
            "name": instance_name,
            "description": f"Custom instance with {len(locations)} locations",
            "locations": [loc['id'] for loc in locations]
        }
        
        return instance
    
    def compute_distance_matrix(self, location_ids: List[int]) -> np.ndarray:
        """
        Compute distance matrix for given location IDs.
        Uses Google Maps driving distance if available, otherwise geodesic.
        
        Args:
            location_ids: List of location IDs to include
            
        Returns:
            NxN distance matrix in kilometers
        """
        # Get location details for the given IDs
        locations = []
        for loc_id in location_ids:
            location = next(loc for loc in self.locations if loc["id"] == loc_id)
            locations.append(location)
        
        # Use the distance calculator
        return self.distance_calculator.compute_distance_matrix(locations)
    
    def run_solver_on_instance(self, solver: BaseSolver, instance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single solver on a test instance.
        
        Args:
            solver: TSP solver instance
            instance: Test instance dictionary
            
        Returns:
            Dictionary with results
        """
        location_ids = instance["locations"]
        distance_matrix = self.compute_distance_matrix(location_ids)
        
        # Get location details for the instance
        instance_locations = []
        for loc_id in location_ids:
            location = next(loc for loc in self.locations if loc["id"] == loc_id)
            instance_locations.append(location)
        
        # Solve
        route, total_distance = solver.solve(distance_matrix, instance_locations)
        
        # Convert route indices to location IDs for output
        route_location_ids = [location_ids[i] for i in route]
        
        # Get route details if using Google Maps
        route_details = self.distance_calculator.get_route_details(instance_locations, route)
        
        result = {
            "solver_name": solver.name,
            "instance_name": instance["name"],
            "route": route,
            "route_location_ids": route_location_ids,
            "route_locations": [instance_locations[i] for i in route],
            "total_distance": total_distance,
            "solve_time": solver.get_solve_time(),
            "num_locations": len(location_ids)
        }
        
        if route_details:
            result["route_details"] = route_details
        
        return result
    
    def compare_solvers(self, solvers: List[BaseSolver]) -> List[Dict[str, Any]]:
        """
        Compare multiple solvers on all test instances.
        
        Args:
            solvers: List of solver instances
            
        Returns:
            List of result dictionaries
        """
        if not self.test_instances:
            self.load_test_instances()
        
        results = []
        
        for instance in self.test_instances:
            print(f"\nTesting instance: {instance['name']}")
            print(f"Locations: {len(instance['locations'])}")
            
            for solver in solvers:
                print(f"  Running {solver.name}...")
                result = self.run_solver_on_instance(solver, instance)
                results.append(result)
                
                print(f"    Distance: {result['total_distance']:.2f} km")
                print(f"    Time: {result['solve_time']:.4f} seconds")
        
        self.results = results
        return results
    
    def generate_comparison_report(self) -> pd.DataFrame:
        """
        Generate a comparison report as a pandas DataFrame.
        
        Returns:
            DataFrame with solver comparison results
        """
        if not self.results:
            raise ValueError("No results available. Run compare_solvers() first.")
        
        df = pd.DataFrame(self.results)
        
        # Pivot table for easier comparison
        pivot_df = df.pivot_table(
            index='instance_name',
            columns='solver_name',
            values=['total_distance', 'solve_time'],
            aggfunc='first'
        )
        
        return pivot_df
    
    def print_comparison_summary(self) -> None:
        """Print a summary of solver comparison results."""
        if not self.results:
            print("No results available. Run compare_solvers() first.")
            return
        
        df = pd.DataFrame(self.results)
        
        print("\n" + "="*60)
        print("SOLVER COMPARISON SUMMARY")
        print("="*60)
        
        # Group by solver and calculate averages
        summary = df.groupby('solver_name').agg({
            'total_distance': ['mean', 'std'],
            'solve_time': ['mean', 'std'],
            'num_locations': 'first'
        }).round(4)
        
        print(summary)
        
        # Best solver for each instance
        print("\nBest solver per instance:")
        for instance in df['instance_name'].unique():
            instance_df = df[df['instance_name'] == instance]
            best_solver = instance_df.loc[instance_df['total_distance'].idxmin()]
            print(f"  {instance}: {best_solver['solver_name']} "
                  f"({best_solver['total_distance']:.2f} km)")
    
    def visualize_results(self, results: List[Dict[str, Any]] = None) -> None:
        """
        Visualize results using the map visualizer.
        
        Args:
            results: Results to visualize (uses self.results if None)
        """
        if results is None:
            results = self.results
        
        if not results:
            print("No results to visualize. Run compare_solvers() first.")
            return
        
        from visualization.map_visualizer import MapVisualizer
        visualizer = MapVisualizer(self.locations)
        
        # Group results by instance
        instances = {}
        for result in results:
            instance_name = result['instance_name']
            if instance_name not in instances:
                instances[instance_name] = []
            instances[instance_name].append(result)
        
        # Visualize each instance
        for instance_name, instance_results in instances.items():
            print(f"\nVisualizing {instance_name}...")
            visualizer.visualize_routes(instance_results, instance_name)


def main():
    """Main function to run solver comparison."""
    runner = SolverRunner()
    
    # Initialize solvers
    solvers = [
        NearestNeighborSolver(),
        ORToolsSolver("first_solution"),
        ORToolsSolver("local_search")
    ]
    
    # Run comparison
    results = runner.compare_solvers(solvers)
    
    # Generate report
    runner.print_comparison_summary()
    
    # Visualize results
    runner.visualize_results(results)


if __name__ == "__main__":
    main()
