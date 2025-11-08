#!/usr/bin/env python3
"""
TSP solver that runs a single specified solver.

Usage:
    python solve_tsp_single_solver.py <locations_file> <solver_name> [region]
    
Example:
    python solve_tsp_single_solver.py jc_locations.txt branch_and_bound sg
    
Available solvers:
    - nearest_neighbor
    - held_karp
    - branch_and_bound
    - rl_solver
"""

import sys
from typing import List
from runner.solver_runner import SolverRunner
from utils.solver_factory import get_solver_specs, instantiate_solvers


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
    if len(sys.argv) < 3:
        print("Usage: python solve_tsp_single_solver.py <locations_file> <solver_name> [region]")
        print("\nExample:")
        print("  python solve_tsp_single_solver.py jc_locations.txt branch_and_bound sg")
        print("\nAvailable solvers:")
        print("  - nearest_neighbor")
        print("  - held_karp")
        print("  - branch_and_bound")
        print("  - rl_solver")
        sys.exit(1)
    
    filename = sys.argv[1]
    solver_name = sys.argv[2]
    region = sys.argv[3] if len(sys.argv) > 3 else "sg"
    
    # Read locations
    print(f"\n📍 Reading locations from: {filename}")
    locations = read_locations_from_file(filename)
    
    if len(locations) < 2:
        print("❌ Error: Need at least 2 locations")
        sys.exit(1)
    
    print(f"✓ Found {len(locations)} locations")
    
    # Get the solver
    available_specs = get_solver_specs(include_unavailable=True)
    available_slugs = [spec["slug"] for spec in available_specs if spec["available"]]

    if solver_name not in available_slugs:
        print(f"❌ Error: Unknown or unavailable solver '{solver_name}'")
        print("\nAvailable solvers:")
        for spec in available_specs:
            status = " (missing dependencies)" if not spec["available"] else ""
            print(f"  - {spec['slug']}{status}")
        sys.exit(1)

    print(f"\n🔧 Using solver: {solver_name}")
    try:
        solver = instantiate_solvers([solver_name])[0]
    except ValueError as exc:
        print(f"❌ Error: {exc}")
        sys.exit(1)
    
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
    
    # Run the solver
    print(f"\n⚙️  Running {solver.name}...")
    result = runner.run_solver_on_instance(solver, instance)
    
    # Print results
    print(f"\n{'='*70}")
    print(f"✅ SOLUTION: {result['solver_name']}")
    print(f"{'='*70}")
    print(f"Total Distance: {result['total_distance']:.2f} km")
    print(f"Solve Time: {result['solve_time']:.4f} seconds")
    
    print(f"\n{'='*70}")
    print(f"🗺️  OPTIMAL ROUTE")
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
    
    # Generate visualization
    runner.visualize_results([result])


if __name__ == "__main__":
    main()

