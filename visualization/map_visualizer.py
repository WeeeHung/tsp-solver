import folium
from typing import List, Dict, Any, Optional
import os
import json
import urllib.parse


class MapVisualizer:
    """
    Folium-based map visualizer for TSP routes.
    """
    
    def __init__(self, locations: List[Dict[str, Any]]):
        """
        Initialize visualizer with location data.
        
        Args:
            locations: List of location dictionaries with 'id', 'name', 'lat', 'lon'
        """
        self.locations = locations
        self.location_dict = {loc["id"]: loc for loc in locations}
        
        # Singapore center coordinates
        self.center_lat = 1.3521
        self.center_lon = 103.8198
    
    def create_base_map(self, instance_name: str = "TSP Route") -> folium.Map:
        """
        Create base map centered on Singapore.
        
        Args:
            instance_name: Name for the map title
            
        Returns:
            Folium map object
        """
        m = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # Add title
        title_html = f'''
        <h3 align="center" style="font-size:20px"><b>{instance_name}</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        return m
    
    def add_locations(self, map_obj: folium.Map, location_ids: List[int], 
                     color: str = 'blue', size: int = 8) -> None:
        """
        Add location markers to the map.
        
        Args:
            map_obj: Folium map object
            location_ids: List of location IDs to add
            color: Color for markers
            size: Size of markers
        """
        for i, loc_id in enumerate(location_ids):
            location = self.location_dict[loc_id]
            
            # Different marker for depot (first location)
            if i == 0:
                marker_color = 'red'
                icon = 'home'
            else:
                marker_color = color
                icon = 'info-sign'
            
            folium.Marker(
                [location["lat"], location["lon"]],
                popup=f"{i}: {location['name']}",
                tooltip=f"{i}: {location['name']}",
                icon=folium.Icon(color=marker_color, icon=icon)
            ).add_to(map_obj)
    
    def add_route(self, map_obj: folium.Map, route: List[int], 
                 color: str = 'blue', weight: int = 3, opacity: float = 0.7) -> None:
        """
        Add route lines to the map.
        
        Args:
            map_obj: Folium map object
            route: List of location IDs in visit order
            color: Color for route lines
            weight: Thickness of route lines
            opacity: Opacity of route lines
        """
        if len(route) < 2:
            return
        
        # Convert route indices to coordinates
        coordinates = []
        for loc_id in route:
            location = self.location_dict[loc_id]
            coordinates.append([location["lat"], location["lon"]])
        
        # Add route line
        folium.PolyLine(
            coordinates,
            color=color,
            weight=weight,
            opacity=opacity,
            popup=f"Route: {len(route)-1} stops"
        ).add_to(map_obj)
    
    def visualize_single_route(self, route: List[int], location_ids: List[int],
                             solver_name: str, total_distance: float,
                             instance_name: str = "TSP Route") -> folium.Map:
        """
        Visualize a single route.
        
        Args:
            route: List of location IDs in visit order
            location_ids: List of all location IDs in the instance
            solver_name: Name of the solver
            total_distance: Total distance of the route
            instance_name: Name of the instance
            
        Returns:
            Folium map object
        """
        m = self.create_base_map(f"{instance_name} - {solver_name}")
        
        # Add locations
        self.add_locations(m, location_ids)
        
        # Add route
        self.add_route(m, route)
        
        # Add distance info
        distance_html = f'''
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 200px; height: 60px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <b>{solver_name}</b><br>
        Distance: {total_distance:.2f} km<br>
        Stops: {len(route)-1}
        </div>
        '''
        m.get_root().html.add_child(folium.Element(distance_html))
        
        return m
    
    def visualize_routes(self, results: List[Dict[str, Any]], 
                       instance_name: str = "TSP Routes",
                       save_route_sequences: bool = True) -> None:
        """
        Visualize routes by saving route sequences and Google Maps links.
        
        Args:
            results: List of result dictionaries from solver comparison
            instance_name: Name of the instance
            save_route_sequences: If True, save route sequences to JSON file
        """
        if not results:
            print("No results to visualize")
            return
        
        output_dir = "visualization/output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save route sequences
        if save_route_sequences:
            self._save_route_sequences(results, instance_name, output_dir)
        
        # Create Google Maps link for best route
        self._create_google_maps_link(results, instance_name, output_dir)
    
    def save_map(self, map_obj: folium.Map, filename: str) -> None:
        """
        Save map to HTML file.
        
        Args:
            map_obj: Folium map object
            filename: Output filename
        """
        output_dir = "visualization/output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)
        map_obj.save(output_path)
        print(f"Map saved to: {output_path}")
    
    def _save_route_sequences(self, results: List[Dict[str, Any]], 
                             instance_name: str, output_dir: str) -> None:
        """
        Save route sequences to JSON file for analysis.
        
        Args:
            results: List of result dictionaries
            instance_name: Name of the instance
            output_dir: Output directory
        """
        route_data = {
            "instance_name": instance_name,
            "routes": []
        }

        # if there is "held_karp" in the results, take the total_distance of the held_karp result as golden
        # to calculate the optimality gap percentage of the other solvers
        golden_distance = None
        for result in results:
            if result["solver_name"] == "Held-Karp (DP)":
                golden_distance = result["total_distance"]
                break
        if golden_distance is not None:
            for result in results:
                result["optimality_gap_percent"] = (
                    abs(result["total_distance"] - golden_distance) / golden_distance
                ) * 100


        for result in results:
            route_info = {
                "solver_name": result["solver_name"],
                "total_distance_km": result["total_distance"],
                "solve_time_seconds": result.get("solve_time", 0),
                "num_locations": result.get("num_locations", 0),
                "optimality_gap_percent": result.get("optimality_gap_percent", 0),
                "sequence": []
            }
            
            # Add location details in visit order
            if "route_locations" in result:
                for i, loc in enumerate(result["route_locations"]):
                    route_info["sequence"].append({
                        "order": i,
                        "location_id": loc["id"],
                        "name": loc["name"],
                        "latitude": loc["lat"],
                        "longitude": loc["lon"]
                    })
            else:
                # Fallback if route_locations not available
                for i, loc_id in enumerate(result["route"]):
                    loc = self.location_dict.get(loc_id)
                    if loc:
                        route_info["sequence"].append({
                            "order": i,
                            "location_id": loc["id"],
                            "name": loc["name"],
                            "latitude": loc["lat"],
                            "longitude": loc["lon"]
                        })
            
            # Add route details if available (from Google Maps Directions API)
            if "route_details" in result:
                route_info["google_maps_details"] = {
                    "total_distance_km": result["route_details"]["distance_km"],
                    "total_duration_minutes": result["route_details"]["duration_minutes"],
                    "polyline": result["route_details"]["polyline"]
                }
            
            route_data["routes"].append(route_info)
        
        # Save to JSON file
        output_file = os.path.join(output_dir, f"{instance_name.replace(' ', '_').lower()}_routes.json")
        with open(output_file, 'w') as f:
            json.dump(route_data, f, indent=2)
        
        print(f"Route sequences saved to: {output_file}")
    
    def _create_google_maps_link(self, results: List[Dict[str, Any]], 
                                 instance_name: str, output_dir: str) -> None:
        """
        Create Google Maps link for the best route.
        
        Args:
            results: List of result dictionaries
            instance_name: Name of the instance
            output_dir: Output directory
        """
        if not results:
            return
        
        # Find the best route (shortest distance)
        best_result = min(results, key=lambda x: x["total_distance"])
        
        # Get route locations
        if "route_locations" not in best_result:
            return
        
        locations = best_result["route_locations"]
        
        # Build Google Maps directions URL
        # Format: https://www.google.com/maps/dir/?api=1&origin=...&destination=...&waypoints=...
        
        if len(locations) < 2:
            return
        
        origin = f"{locations[0]['lat']},{locations[0]['lon']}"
        destination = f"{locations[-1]['lat']},{locations[-1]['lon']}"
        
        # Waypoints (intermediate stops)
        waypoints = []
        if len(locations) > 2:
            for loc in locations[1:-1]:
                waypoints.append(f"{loc['lat']},{loc['lon']}")
        
        # Build URL
        base_url = "https://www.google.com/maps/dir/?api=1"
        url_parts = [
            base_url,
            f"origin={urllib.parse.quote(origin)}",
            f"destination={urllib.parse.quote(destination)}",
            "travelmode=driving"
        ]
        
        if waypoints:
            waypoints_str = "|".join(waypoints)
            url_parts.append(f"waypoints={urllib.parse.quote(waypoints_str)}")
        
        google_maps_url = "&".join(url_parts)
        
        # Save URL to text file
        output_file = os.path.join(output_dir, f"{instance_name.replace(' ', '_').lower()}_google_maps_link.txt")
        with open(output_file, 'w') as f:
            f.write(f"Google Maps Route for Best Solution\n")
            f.write(f"=====================================\n\n")
            f.write(f"Instance: {instance_name}\n")
            f.write(f"Best Solver: {best_result['solver_name']}\n")
            f.write(f"Total Distance: {best_result['total_distance']:.2f} km\n\n")
            f.write(f"Route Sequence:\n")
            for i, loc in enumerate(locations):
                f.write(f"  {i+1}. {loc['name']} ({loc['lat']}, {loc['lon']})\n")
            f.write(f"\n\nGoogle Maps URL:\n")
            f.write(f"{google_maps_url}\n\n")
            f.write(f"Note: Google Maps may optimize waypoint order. Our TSP solution maintains the exact sequence above.\n")
        
        print(f"Google Maps link saved to: {output_file}")
        print(f"\nYou can open this URL in your browser to view the route in Google Maps:")
        print(f"{google_maps_url}")
