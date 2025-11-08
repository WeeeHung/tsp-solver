# TSP Route Planning with Google Maps

A simple route planning system that solves the Travelling Salesman Problem using **actual driving distances** from Google Maps. Just provide location names in a text file!

## Features

- 🚗 **Real Driving Distances**: Uses Google Maps Distance Matrix API
- 📝 **Simple Text Input**: List locations in a text file, one per line
- 🌍 **Automatic Geocoding**: Converts location names to coordinates
- 🗺️ **Google Maps Links**: Get direct links to view routes
- 💾 **Smart Caching**: Minimizes API costs with automatic caching
- 🧮 **Multiple Solvers**: Compare classical TSP algorithms
  - Nearest Neighbor (Greedy Heuristic)
  - Held-Karp (Dynamic Programming - Optimal)
  - Branch & Bound (Tree Search with Pruning - Optimal)
  - Reinforcement Learning Solver (requires PyTorch)

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Maps API

1. Get API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable these APIs:
   - Distance Matrix API
   - Directions API
   - Geocoding API
3. Enable billing (you get $200 free credit/month)
4. Create `.env` file:

```bash
cp env.example .env
# Edit .env and add: GOOGLE_MAPS_API_KEY=your_key_here
```

### 3. Create Locations File

Create a text file with locations (one per line):

**my_locations.txt:**

```
Marina Bay Sands, Singapore
Gardens by the Bay, Singapore
Singapore Flyer
Merlion Park, Singapore
Raffles Hotel, Singapore
```

### 4. Run

```bash
python solve_tsp.py my_locations.txt sg
```

Where:

- `my_locations.txt` = your locations file
- `sg` = region code (optional, default: `sg`)

#### Run a single solver

Use the single-runner script to benchmark one algorithm at a time:

```bash
python solve_tsp_single_solver.py my_locations.txt branch_and_bound sg
```

Where:

- `my_locations.txt` = your locations file
- `branch_and_bound` = solver (`nearest_neighbor`, `held_karp`, `branch_and_bound`, or `rl_solver`)
- `sg` = region code (optional, default: `sg`)

> ℹ️ `rl_solver` depends on the RL model in `train/` and requires extra packages (e.g., `torch`, `matplotlib`). Install them via `pip install -r requirements.txt` plus the optional training dependencies if you want to enable it.

## Example Output

```
======================================================================
📊 SOLVER COMPARISON
======================================================================

Rank   Solver                    Distance (km)   Time (s)
----------------------------------------------------------------------
1      Held-Karp (DP)            12.45           0.0234
2      Branch & Bound            12.45           0.0156
3      Nearest Neighbor          13.21           0.0012

======================================================================
✅ BEST SOLUTION: Branch & Bound
======================================================================
Total Distance: 12.45 km
Solve Time: 0.0156 seconds

======================================================================
🗺️  OPTIMAL ROUTE
======================================================================
START: Marina Bay Sands
  2.   Gardens by the Bay
  3.   Singapore Flyer
  4.   Merlion Park
  5.   Raffles Hotel
END:   Marina Bay Sands (back to start)

======================================================================
💾 SAVED FILES
======================================================================
✓ Route details: visualization/output/tsp_tour_(5_stops)_routes.json
✓ Google Maps link: visualization/output/tsp_tour_(5_stops)_google_maps_link.txt
✓ Cached locations: data/custom_locations.json
```

## Output Files

All files saved in `visualization/output/`:

1. **`*_routes.json`** - Complete route with coordinates and distances
2. **`*_google_maps_link.txt`** - Direct URL to view route in Google Maps
3. **`data/custom_locations.json`** - Cached geocoded locations

## Examples

### Singapore Tour

**singapore.txt:**

```
Marina Bay Sands, Singapore
Gardens by the Bay, Singapore
Singapore Flyer
Merlion Park, Singapore
Sentosa Island, Singapore
```

```bash
python solve_tsp.py singapore.txt sg
```

### New York Tour

**nyc.txt:**

```
Statue of Liberty, New York
Times Square, New York
Central Park, New York
Empire State Building, New York
Brooklyn Bridge, New York
```

```bash
python solve_tsp.py nyc.txt us
```

### Tokyo Tour

**tokyo.txt:**

```
Tokyo Tower, Tokyo
Senso-ji Temple, Tokyo
Shibuya Crossing, Tokyo
Tokyo Skytree, Tokyo
Meiji Shrine, Tokyo
```

```bash
python solve_tsp.py tokyo.txt jp
```

## Region Codes

Use these codes for better geocoding accuracy:

| Code | Region         | Code | Region  |
| ---- | -------------- | ---- | ------- |
| `sg` | Singapore      | `us` | USA     |
| `uk` | United Kingdom | `jp` | Japan   |
| `au` | Australia      | `ca` | Canada  |
| `fr` | France         | `de` | Germany |
| `it` | Italy          | `es` | Spain   |

Full list: [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)

## Troubleshooting

### "API key not found"

Create `.env` file:

```bash
echo "GOOGLE_MAPS_API_KEY=your_actual_key" > .env
```

### "REQUEST_DENIED"

Enable required APIs:

1. Go to https://console.cloud.google.com/apis/library
2. Search and enable:
   - Distance Matrix API
   - Directions API
   - Geocoding API
3. Wait 1-2 minutes

### "No results found for location"

Make location names more specific:

- ✅ "Marina Bay Sands, Singapore"
- ✅ "350 Orchard Road, Singapore"
- ❌ "that hotel" or "downtown"

### Billing Not Enabled

1. Go to https://console.cloud.google.com/billing
2. Link a billing account
3. Note: Required even for free tier ($200/month credit)

## How It Works

1. **Geocoding**: Converts location names to coordinates (Geocoding API)
2. **Distance Calculation**: Gets actual driving distances (Distance Matrix API)
3. **Optimization**: Solves TSP using multiple classical algorithms and compares results
4. **Results**: Saves route details and Google Maps link (Directions API)

## TSP Algorithms

The system compares multiple classical TSP solving algorithms:

### 1. Nearest Neighbor (Greedy Heuristic)

- **Strategy**: Start at depot, always visit the nearest unvisited location
- **Time Complexity**: O(n²)
- **Quality**: Fast but suboptimal (typically 20-40% above optimal)
- **Best for**: Quick approximations, large instances (n > 20)

### 2. Held-Karp (Dynamic Programming)

- **Strategy**: Exact algorithm using bitmask DP to explore all possible subsets
- **Time Complexity**: O(n² × 2ⁿ)
- **Space Complexity**: O(n × 2ⁿ)
- **Quality**: Guaranteed optimal solution
- **Best for**: Small instances (n ≤ 20), when optimality is critical

### 3. Branch & Bound (Tree Search)

- **Strategy**: Systematic tree search with intelligent pruning using MST lower bounds
- **Time Complexity**: O(n!) worst case, much better in practice
- **Quality**: Guaranteed optimal solution with pruning
- **Best for**: Medium instances (n ≤ 20), often faster than Held-Karp

### Algorithm Comparison

| Algorithm        | Type           | Optimal? | Time                | Best Use Case                         |
| ---------------- | -------------- | -------- | ------------------- | ------------------------------------- |
| Nearest Neighbor | Heuristic      | ❌       | O(n²)               | Large instances, quick results        |
| Held-Karp        | Exact (DP)     | ✅       | O(n² × 2ⁿ)          | Small instances, guaranteed optimal   |
| Branch & Bound   | Exact (Search) | ✅       | O(n!) worst, pruned | Medium instances, often fastest exact |

**Note**: OR-Tools solver is excluded from comparisons as it uses advanced metaheuristics
which would be "cheating" when exploring classical algorithms.

## Creating Custom Solvers

Want to implement your own TSP algorithm? Here's how:

### 1. Inherit from BaseSolver

Create a new file in `solvers/` directory:

```python
# solvers/my_solver.py
import time
import numpy as np
from typing import List, Dict, Any, Tuple
from .base_solver import BaseSolver

class MySolver(BaseSolver):
    def __init__(self):
        super().__init__("My Custom Solver")

    def solve(self, distance_matrix: np.ndarray, locations: List[Dict[str, Any]]) -> Tuple[List[int], float]:
        start_time = time.time()

        # Your algorithm here
        n = len(locations)
        route = list(range(n)) + [0]  # Example: sequential route

        # Calculate total distance
        total_distance = sum(distance_matrix[route[i]][route[i+1]]
                            for i in range(len(route)-1))

        self.solve_time = time.time() - start_time
        return route, total_distance
```

### 2. Input/Output Format

**Input**:

- `distance_matrix`: NxN numpy array of distances in km
  ```python
  [[0.0, 5.2, 8.1],
   [5.2, 0.0, 6.3],
   [8.1, 6.3, 0.0]]
  ```
- `locations`: List of location dictionaries
  ```python
  [{"id": 0, "name": "Location A", "lat": 1.23, "lon": 103.45}, ...]
  ```

**Output**:

- `route`: List starting and ending at 0 (depot)
  ```python
  [0, 2, 1, 0]  # Start at 0 → visit 2 → visit 1 → return to 0
  ```
- `total_distance`: Total route distance in km (float)

### 3. Add to Solver Runner

Update `runner/solver_runner.py` in the `get_all_solvers()` method:

```python
try:
    from solvers.my_solver import MySolver
    solvers.append(MySolver())
except ImportError:
    pass
```

Your solver will now be automatically included in comparisons!

## Text File Format

### Basic

```
Location 1
Location 2
Location 3
```

### With Comments

```
# My Singapore Tour
Marina Bay Sands, Singapore
Gardens by the Bay, Singapore

# Cultural sites
Chinatown, Singapore
Little India, Singapore
```

### Tips

- One location per line
- Add city/country for better accuracy
- Lines starting with `#` are ignored
- Empty lines are ignored

## Project Structure

```
Project/
├── solve_tsp.py              # Main script
├── requirements.txt          # Dependencies
├── env.example               # API key template
├── example_locations.txt     # Sample locations
├── data/
│   ├── distance_cache.json   # Cached distances
│   └── geocode_cache.json    # Cached coordinates
├── solvers/
│   ├── base_solver.py        # Abstract base class with examples
│   ├── nearest_neighbor.py   # Greedy heuristic O(n²)
│   ├── held_karp.py          # DP exact solver O(n²×2ⁿ)
│   ├── branch_and_bound.py   # Tree search exact solver
│   └── ortools_solver.py     # (Excluded from comparisons)
├── runner/
│   └── solver_runner.py
├── utils/
│   ├── distance_calculator.py
│   └── geocoder.py
└── visualization/
    ├── map_visualizer.py
    └── output/               # Generated files
        ├── *_routes.json
        └── *_google_maps_link.txt
```

## Requirements

- Python 3.11+
- Google Maps API key
- Internet connection
- Dependencies in `requirements.txt`

## License

MIT
