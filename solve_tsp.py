#!/usr/bin/env python3
"""
Simple TSP solver that reads locations from a text file.

Usage:
    python solve_tsp.py locations.txt [region]
    
Example:
    python solve_tsp.py my_locations.txt sg
"""

import sys
from typing import List
from solvers.ortools_solver import ORToolsSolver
from runner.solver_runner import SolverRunner


def read_locations_from_file(filename: str) -> List[str]:
    """Read locations from a text file (one per line)."""
    try:
        with open(filename, 'r') as f:
            locations = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        return locations
    except FileNotFoundError:
        print(f"❌ Error: File '{filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python solve_tsp.py <locations_file> [region]")
        print("\nExample:")
        print("  python solve_tsp.py my_locations.txt sg")
        print("\nThe locations file should contain one location per line.")
        sys.exit(1)
    
    filename = sys.argv[1]
    region = sys.argv[2] if len(sys.argv) > 2 else "sg"
    
    # Read locations
    print(f"\n📍 Reading locations from: {filename}")
    locations = read_locations_from_file(filename)
    
    if len(locations) < 2:
        print("❌ Error: Need at least 2 locations")
        sys.exit(1)
    
    print(f"✓ Found {len(locations)} locations")
    
    # Initialize runner
    print(f"\n🌍 Geocoding locations (region: {region})...")
    runner = SolverRunner(use_google_maps=True)
    
    try:
        runner.load_locations_from_names(
            location_names=locations,
            region=region,
            save_to_file="custom_locations.json"
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    if not runner.locations:
        print("❌ No locations were successfully geocoded")
        sys.exit(1)
    
    # Create instance
    instance_name = f"TSP Tour ({len(locations)} stops)"
    instance = runner.create_custom_instance(
        location_names=locations,
        instance_name=instance_name
    )
    
    # Solve with optimized solver
    print(f"\n🔧 Solving TSP with OR-Tools...")
    solver = ORToolsSolver("local_search")
    result = runner.run_solver_on_instance(solver, instance)
    
    # Print results
    print(f"\n{'='*70}")
    print(f"✅ SOLUTION")
    print(f"{'='*70}")
    print(f"Total Distance: {result['total_distance']:.2f} km")
    print(f"Solve Time: {result['solve_time']:.4f} seconds")
    
    print(f"\n{'='*70}")
    print(f"🗺️  ROUTE")
    print(f"{'='*70}")
    
    if 'route_locations' in result:
        for i, loc in enumerate(result['route_locations'], 1):
            if i == 1:
                print(f"START: {loc['name']}")
            elif i == len(result['route_locations']):
                print(f"END:   {loc['name']} (back to start)")
            else:
                print(f"  {i}.   {loc['name']}")
    
    # Save results
    print(f"\n{'='*70}")
    print(f"💾 SAVED FILES")
    print(f"{'='*70}")
    print(f"✓ Route details: visualization/output/{instance_name.replace(' ', '_').lower()}_routes.json")
    print(f"✓ Google Maps link: visualization/output/{instance_name.replace(' ', '_').lower()}_google_maps_link.txt")
    print(f"✓ Cached locations: data/custom_locations.json")
    print()
    
    # Generate visualizations (without HTML)
    runner.visualize_results([result])


if __name__ == "__main__":
    main()

