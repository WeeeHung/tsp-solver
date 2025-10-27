import os
import json
import numpy as np
import googlemaps
from typing import List, Dict, Any, Optional, Tuple
from geopy.distance import geodesic
from dotenv import load_dotenv
import hashlib
import time


class DistanceCalculator:
    """
    Distance calculator that supports both geodesic and Google Maps driving distances.
    Includes caching to minimize API calls.
    """
    
    def __init__(self, use_google_maps: bool = True, cache_file: str = "data/distance_cache.json"):
        """
        Initialize distance calculator.
        
        Args:
            use_google_maps: If True, use Google Maps Distance Matrix API
            cache_file: Path to cache file for storing distance calculations
        """
        self.use_google_maps = use_google_maps
        self.cache_file = cache_file
        self.cache = {}
        self.gmaps_client = None
        
        # Load environment variables
        load_dotenv()
        
        if use_google_maps:
            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            if not api_key:
                print("\n" + "="*70)
                print("⚠️  WARNING: GOOGLE_MAPS_API_KEY not found in environment variables")
                print("="*70)
                print("Falling back to geodesic (straight-line) distance calculation.")
                print("\nTo use Google Maps driving distances:")
                print("  1. Copy env.example to .env")
                print("  2. Add your Google Maps API key to .env")
                print("  3. Run: python test_google_maps_setup.py")
                print("="*70 + "\n")
                self.use_google_maps = False
            elif api_key == 'your_api_key_here':
                print("\n" + "="*70)
                print("⚠️  WARNING: API key not configured in .env file")
                print("="*70)
                print("Please replace 'your_api_key_here' with your actual API key.")
                print("Run: python test_google_maps_setup.py")
                print("="*70 + "\n")
                self.use_google_maps = False
            else:
                self.gmaps_client = googlemaps.Client(key=api_key)
                print("✅ Google Maps API initialized successfully")
        
        # Load cache if exists
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load distance cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                print(f"Loaded {len(self.cache)} cached distance calculations")
            except Exception as e:
                print(f"Warning: Could not load cache file: {e}")
                self.cache = {}
    
    def _save_cache(self) -> None:
        """Save distance cache to file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache file: {e}")
    
    def _get_cache_key(self, lat1: float, lon1: float, lat2: float, lon2: float) -> str:
        """Generate cache key for a pair of coordinates."""
        # Round to 6 decimal places for cache key (about 0.11m precision)
        coords = f"{lat1:.6f},{lon1:.6f}|{lat2:.6f},{lon2:.6f}"
        return hashlib.md5(coords.encode()).hexdigest()
    
    def _get_geodesic_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate geodesic distance in kilometers."""
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers
    
    def _get_google_maps_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Get driving distance from Google Maps Distance Matrix API.
        
        Returns:
            Distance in kilometers
        """
        cache_key = self._get_cache_key(lat1, lon1, lat2, lon2)
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Call Distance Matrix API
            result = self.gmaps_client.distance_matrix(
                origins=[(lat1, lon1)],
                destinations=[(lat2, lon2)],
                mode="driving",
                units="metric"
            )
            
            # Extract distance
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                distance_meters = result['rows'][0]['elements'][0]['distance']['value']
                distance_km = distance_meters / 1000.0
                
                # Cache the result
                self.cache[cache_key] = distance_km
                return distance_km
            else:
                # Fallback to geodesic if API fails
                status = result['rows'][0]['elements'][0]['status']
                if not hasattr(self, '_error_shown'):
                    print(f"\n⚠️  Warning: Google Maps API returned {status}")
                    print("   Falling back to geodesic distance for remaining calculations.")
                    self._error_shown = True
                distance_km = self._get_geodesic_distance(lat1, lon1, lat2, lon2)
                return distance_km
                
        except googlemaps.exceptions.ApiError as e:
            if not hasattr(self, '_api_error_shown'):
                print("\n" + "="*70)
                print("❌ Google Maps API Error")
                print("="*70)
                print(f"Error: {e}")
                print("\n📋 This usually means:")
                print("   1. Distance Matrix API is NOT ENABLED in Google Cloud Console")
                print("   2. Billing is not set up (required even for free tier)")
                print("   3. API key has restrictions blocking this API")
                print("\n🔧 To fix:")
                print("   1. Run: python test_google_maps_setup.py")
                print("   2. Follow the diagnostic instructions")
                print("\n   Quick fix: https://console.cloud.google.com/apis/library")
                print("   → Search 'Distance Matrix API' → Click ENABLE")
                print("="*70)
                print("\n⚠️  Falling back to geodesic distance for this run.\n")
                self._api_error_shown = True
            distance_km = self._get_geodesic_distance(lat1, lon1, lat2, lon2)
            return distance_km
            
        except Exception as e:
            if not hasattr(self, '_general_error_shown'):
                print(f"\n⚠️  Warning: Error calling Google Maps API: {e}")
                print("   Falling back to geodesic distance.")
                self._general_error_shown = True
            distance_km = self._get_geodesic_distance(lat1, lon1, lat2, lon2)
            return distance_km
    
    def compute_distance_matrix(self, locations: List[Dict[str, Any]]) -> np.ndarray:
        """
        Compute distance matrix for given locations.
        
        Args:
            locations: List of location dictionaries with 'lat' and 'lon' keys
            
        Returns:
            NxN distance matrix in kilometers
        """
        n = len(locations)
        distance_matrix = np.zeros((n, n))
        
        print(f"Computing distance matrix for {n} locations...")
        print(f"Using {'Google Maps driving distance' if self.use_google_maps else 'geodesic distance'}")
        
        # Track API calls for rate limiting
        api_calls = 0
        start_time = time.time()
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    lat1, lon1 = locations[i]["lat"], locations[i]["lon"]
                    lat2, lon2 = locations[j]["lat"], locations[j]["lon"]
                    
                    if self.use_google_maps and self.gmaps_client:
                        distance = self._get_google_maps_distance(lat1, lon1, lat2, lon2)
                        api_calls += 1
                        
                        # Rate limiting: Google Maps allows 100 requests per second
                        # We'll be conservative with 10 requests per second
                        if api_calls % 10 == 0:
                            time.sleep(0.1)
                    else:
                        distance = self._get_geodesic_distance(lat1, lon1, lat2, lon2)
                    
                    distance_matrix[i][j] = distance
            
            # Progress indicator
            if (i + 1) % 5 == 0 or i == n - 1:
                elapsed = time.time() - start_time
                print(f"  Progress: {i+1}/{n} locations ({elapsed:.1f}s)")
        
        # Save cache after computing
        if self.use_google_maps and self.gmaps_client:
            self._save_cache()
            print(f"Saved cache with {len(self.cache)} entries")
        
        return distance_matrix
    
    def get_route_details(self, locations: List[Dict[str, Any]], 
                         route_indices: List[int]) -> Optional[Dict[str, Any]]:
        """
        Get detailed route information including polyline from Google Maps Directions API.
        
        Args:
            locations: List of location dictionaries
            route_indices: List of location indices in visit order
            
        Returns:
            Dictionary with route details or None if API not available
        """
        if not self.use_google_maps or not self.gmaps_client:
            return None
        
        try:
            # Convert route indices to waypoints
            origin = (locations[route_indices[0]]["lat"], locations[route_indices[0]]["lon"])
            destination = (locations[route_indices[-1]]["lat"], locations[route_indices[-1]]["lon"])
            
            # Google Maps Directions API supports up to 25 waypoints
            # If we have more, we'll need to split the route
            waypoints = []
            if len(route_indices) > 2:
                for idx in route_indices[1:-1]:
                    waypoints.append((locations[idx]["lat"], locations[idx]["lon"]))
            
            # Limit waypoints to 23 (25 total with origin and destination)
            if len(waypoints) > 23:
                # Sample waypoints if too many
                step = len(waypoints) // 23
                waypoints = waypoints[::step][:23]
            
            # Call Directions API
            result = self.gmaps_client.directions(
                origin=origin,
                destination=destination,
                waypoints=waypoints if waypoints else None,
                mode="driving",
                optimize_waypoints=False  # Keep our TSP order
            )
            
            if result and len(result) > 0:
                route = result[0]
                
                # Extract polyline points
                polyline = route['overview_polyline']['points']
                
                # Extract distance and duration
                total_distance = sum(leg['distance']['value'] for leg in route['legs']) / 1000.0  # km
                total_duration = sum(leg['duration']['value'] for leg in route['legs']) / 60.0  # minutes
                
                return {
                    'polyline': polyline,
                    'distance_km': total_distance,
                    'duration_minutes': total_duration,
                    'legs': route['legs']
                }
            
        except Exception as e:
            print(f"Warning: Error getting route details: {e}")
        
        return None

