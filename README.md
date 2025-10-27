# TSP Route Planning with Google Maps

A simple route planning system that solves the Travelling Salesman Problem using **actual driving distances** from Google Maps. Just provide location names in a text file!

## Features

- 🚗 **Real Driving Distances**: Uses Google Maps Distance Matrix API
- 📝 **Simple Text Input**: List locations in a text file, one per line
- 🌍 **Automatic Geocoding**: Converts location names to coordinates
- 🗺️ **Google Maps Links**: Get direct links to view routes
- 💾 **Smart Caching**: Minimizes API costs with automatic caching
- 📊 **Optimized Routes**: Uses OR-Tools for high-quality solutions

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

## Example Output

```
======================================================================
✅ SOLUTION
======================================================================
Total Distance: 12.45 km
Solve Time: 1.2345 seconds

======================================================================
🗺️  ROUTE
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

1. **Geocoding**: Converts location names → coordinates (Geocoding API)
2. **Distances**: Calculates actual driving distances (Distance Matrix API)
3. **Optimization**: Solves TSP using OR-Tools local search
4. **Results**: Saves route details and Google Maps link (Directions API)

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
│   ├── base_solver.py
│   ├── nearest_neighbor.py
│   └── ortools_solver.py
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
