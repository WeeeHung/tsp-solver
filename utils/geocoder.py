import os
import json
import googlemaps
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv


class LocationGeocoder:
    """
    Geocodes location names to coordinates using Google Maps Geocoding API.
    """
    
    def __init__(self, cache_file: str = "data/geocode_cache.json"):
        """
        Initialize geocoder with caching.
        
        Args:
            cache_file: Path to cache file for geocoded locations
        """
        self.cache_file = cache_file
        self.cache = {}
        self.gmaps_client = None
        
        # Load environment variables
        load_dotenv()
        
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError(
                "Google Maps API key required for geocoding.\n"
                "Please set GOOGLE_MAPS_API_KEY in your .env file."
            )
        
        self.gmaps_client = googlemaps.Client(key=api_key)
        print("✅ Geocoding service initialized")
        
        # Load cache if exists
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load geocoding cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                print(f"📦 Loaded {len(self.cache)} cached geocoded locations")
            except Exception as e:
                print(f"⚠️  Warning: Could not load geocode cache: {e}")
                self.cache = {}
    
    def _save_cache(self) -> None:
        """Save geocoding cache to file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save geocode cache: {e}")
    
    def geocode_location(self, location_name: str, region: str = "sg") -> Optional[Dict[str, Any]]:
        """
        Geocode a single location name to coordinates.
        
        Args:
            location_name: Name or address of the location
            region: Region bias for geocoding (default: "sg" for Singapore)
            
        Returns:
            Dictionary with location details or None if geocoding fails
        """
        # Check cache first
        cache_key = f"{location_name.lower()}|{region}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Call Geocoding API
            results = self.gmaps_client.geocode(location_name, region=region)
            
            if not results or len(results) == 0:
                print(f"⚠️  No results found for: {location_name}")
                return None
            
            # Extract first result (most relevant)
            result = results[0]
            location = result['geometry']['location']
            
            location_data = {
                "name": location_name,
                "formatted_address": result['formatted_address'],
                "lat": location['lat'],
                "lon": location['lng'],
                "place_id": result.get('place_id', ''),
                "types": result.get('types', [])
            }
            
            # Cache the result
            self.cache[cache_key] = location_data
            
            return location_data
            
        except googlemaps.exceptions.ApiError as e:
            print(f"❌ Geocoding API Error for '{location_name}': {e}")
            print("\n📋 Make sure Geocoding API is enabled:")
            print("   https://console.cloud.google.com/apis/library/geocoding-backend.googleapis.com")
            return None
            
        except Exception as e:
            print(f"⚠️  Error geocoding '{location_name}': {e}")
            return None
    
    def geocode_locations(self, location_names: List[str], region: str = "sg") -> List[Dict[str, Any]]:
        """
        Geocode multiple location names.
        
        Args:
            location_names: List of location names or addresses
            region: Region bias for geocoding (default: "sg" for Singapore)
            
        Returns:
            List of location dictionaries with coordinates
        """
        print(f"\n🌍 Geocoding {len(location_names)} locations...")
        
        locations = []
        failed = []
        
        for i, name in enumerate(location_names, 1):
            print(f"  [{i}/{len(location_names)}] Geocoding: {name}")
            
            location = self.geocode_location(name, region=region)
            
            if location:
                # Add ID for TSP solver compatibility
                location['id'] = i
                locations.append(location)
                print(f"      ✓ Found: {location['formatted_address']}")
            else:
                failed.append(name)
                print(f"      ✗ Failed to geocode")
        
        # Save cache after geocoding
        if len(self.cache) > 0:
            self._save_cache()
            print(f"\n💾 Saved cache with {len(self.cache)} entries")
        
        if failed:
            print(f"\n⚠️  Failed to geocode {len(failed)} location(s):")
            for name in failed:
                print(f"   - {name}")
        
        print(f"\n✅ Successfully geocoded {len(locations)}/{len(location_names)} locations\n")
        
        return locations
    
    def save_locations_to_json(self, locations: List[Dict[str, Any]], filename: str) -> None:
        """
        Save geocoded locations to JSON file.
        
        Args:
            locations: List of location dictionaries
            filename: Output filename
        """
        output_data = {
            "locations": locations,
            "count": len(locations)
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"💾 Saved {len(locations)} locations to: {filename}")
        except Exception as e:
            print(f"❌ Error saving to {filename}: {e}")


def geocode_from_input(location_names: List[str], output_file: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function to geocode locations from a list of names.
    
    Args:
        location_names: List of location names/addresses
        output_file: Optional file to save geocoded locations
        
    Returns:
        List of geocoded location dictionaries
    """
    geocoder = LocationGeocoder()
    locations = geocoder.geocode_locations(location_names)
    
    if output_file and locations:
        geocoder.save_locations_to_json(locations, output_file)
    
    return locations


# Example usage
if __name__ == "__main__":
    # Example: Geocode some Singapore locations
    sample_locations = [
        "Marina Bay Sands, Singapore",
        "Gardens by the Bay, Singapore",
        "Singapore Flyer",
        "Merlion Park, Singapore",
        "Sentosa Island, Singapore"
    ]
    
    print("=" * 70)
    print("Location Geocoding Example")
    print("=" * 70)
    
    locations = geocode_from_input(
        sample_locations,
        output_file="data/custom_locations.json"
    )
    
    print("\n" + "=" * 70)
    print("Results:")
    print("=" * 70)
    for loc in locations:
        print(f"  {loc['name']}")
        print(f"    Address: {loc['formatted_address']}")
        print(f"    Coordinates: ({loc['lat']}, {loc['lon']})")
        print()

