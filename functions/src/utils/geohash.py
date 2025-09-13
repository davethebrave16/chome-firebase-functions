"""Geohash utility functions for location-based queries using pygeohash library."""

import math
from typing import Tuple, Any, Dict
import pygeohash as pgh
from datetime import datetime


def _convert_firestore_to_json_serializable(data: Any) -> Any:
    """
    Convert Firestore data types to JSON-serializable formats.
    
    Args:
        data: Data to convert (can be dict, list, or primitive)
        
    Returns:
        JSON-serializable data
    """
    if isinstance(data, dict):
        return {key: _convert_firestore_to_json_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_convert_firestore_to_json_serializable(item) for item in data]
    elif hasattr(data, 'isoformat') and callable(getattr(data, 'isoformat')):
        # Handle any datetime-like object with isoformat method
        return data.isoformat()
    elif isinstance(data, datetime):
        # Convert to ISO format string
        return data.isoformat()
    elif hasattr(data, 'path') and hasattr(data, 'id'):
        # Handle DocumentReference objects
        return {
            '_type': 'DocumentReference',
            'id': data.id,
            'path': data.path
        }
    elif hasattr(data, 'latitude') and hasattr(data, 'longitude'):
        # Handle GeoPoint objects - convert to simple lat/lng dict
        return {
            'latitude': data.latitude,
            'longitude': data.longitude
        }
    elif hasattr(data, 'id'):
        # Handle other Firestore objects with id attribute
        return {
            '_type': type(data).__name__,
            'id': data.id
        }
    else:
        return data


def encode_geohash(latitude: float, longitude: float, precision: int = 10) -> str:
    """
    Encode latitude and longitude into a geohash string using pygeohash library.
    
    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        precision: Number of characters in the geohash (1-12, default 10)
        
    Returns:
        Geohash string
        
    Raises:
        ValueError: If coordinates are out of valid range
    """
    if not (-90 <= latitude <= 90):
        raise ValueError(f"Latitude must be between -90 and 90, got {latitude}")
    if not (-180 <= longitude <= 180):
        raise ValueError(f"Longitude must be between -180 and 180, got {longitude}")
    if not (1 <= precision <= 12):
        raise ValueError(f"Precision must be between 1 and 12, got {precision}")
    
    return pgh.encode(latitude, longitude, precision=precision)


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the distance between two points using pygeohash's haversine distance.
    
    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates
        
    Returns:
        Distance in meters
    """
    try:
        # Convert coordinates to geohashes first, then use pygeohash distance
        geohash1 = pgh.encode(lat1, lng1, precision=10)
        geohash2 = pgh.encode(lat2, lng2, precision=10)
        return pgh.geohash_haversine_distance(geohash1, geohash2)
    except Exception as e:
        # Fallback to manual Haversine calculation if pygeohash fails
        print(f"Warning: pygeohash distance calculation failed: {e}, using fallback")
        return _calculate_distance_haversine(lat1, lng1, lat2, lng2)


def _calculate_distance_haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Fallback Haversine distance calculation.
    
    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates
        
    Returns:
        Distance in meters
    """
    # Earth's radius in meters
    R = 6371000
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # Calculate differences
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    # Haversine formula
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def get_geohash_query_bounds(center_lat: float, center_lng: float, radius_meters: float) -> list:
    """
    Get geohash query bounds for a circular area search using pygeohash library.
    
    This implementation uses pygeohash's built-in functions to efficiently
    calculate geohash bounds for circular area searches.
    
    Args:
        center_lat: Center latitude
        center_lng: Center longitude
        radius_meters: Search radius in meters
        
    Returns:
        List of geohash bounds for querying, each with 'startHash' and 'endHash'
    """
    # Determine appropriate precision based on radius
    # Use a coarser precision to ensure we capture all relevant geohashes
    if radius_meters > 1000000:  # > 1000km
        precision = 3
    elif radius_meters > 100000:  # > 100km
        precision = 4
    elif radius_meters > 10000:   # > 10km
        precision = 4  # Use precision 4 for 10km+ to ensure we capture all geohashes
    elif radius_meters > 1000:    # > 1km
        precision = 5
    elif radius_meters > 100:     # > 100m
        precision = 6
    else:
        precision = 7
    
    # Calculate bounding box for the circular area
    # Convert radius from meters to degrees (approximate)
    lat_radius = radius_meters / 111000  # 111000m per degree latitude
    lng_radius = radius_meters / (111000 * math.cos(math.radians(center_lat)))  # Adjust for longitude
    
    # Create bounding box
    min_lat = center_lat - lat_radius
    max_lat = center_lat + lat_radius
    min_lng = center_lng - lng_radius
    max_lng = center_lng + lng_radius
    
    # Use pygeohash to get all geohashes in the bounding box
    try:
        # Create BoundingBox object
        bbox = pgh.BoundingBox(min_lat, min_lng, max_lat, max_lng)
        geohashes = pgh.geohashes_in_box(bbox, precision=precision)
    except Exception as e:
        # Fallback to manual calculation if pygeohash fails
        print(f"Warning: pygeohash.geohashes_in_box failed: {e}, using fallback")
        return _get_geohash_query_bounds_fallback(center_lat, center_lng, radius_meters, precision)
    
    # Filter geohashes to only include those within the actual radius
    filtered_geohashes = []
    for geohash in geohashes:
        # Get the center of this geohash
        geohash_lat, geohash_lng = pgh.decode(geohash)
        
        # Calculate distance from center
        distance = calculate_distance(center_lat, center_lng, geohash_lat, geohash_lng)
        
        # Only include if within radius
        if distance <= radius_meters:
            filtered_geohashes.append(geohash)
    
    # Convert to bounds format - use prefix matching for better coverage
    bounds = []
    for geohash in filtered_geohashes:
        bounds.append({
            "startHash": geohash,
            "endHash": geohash + "~"  # ~ is the last character in base32
        })
    
    return bounds


def _get_geohash_query_bounds_fallback(center_lat: float, center_lng: float, radius_meters: float, precision: int) -> list:
    """
    Fallback implementation for geohash query bounds calculation.
    
    This is used when pygeohash.geohashes_in_box fails.
    """
    # Get center geohash
    center_geohash = encode_geohash(center_lat, center_lng, precision)
    
    # Calculate geohash cell dimensions for this precision
    lat_error = 90.0 / (2 ** (precision * 5 // 2))
    lng_error = 180.0 / (2 ** ((precision * 5 + 1) // 2))
    
    # Calculate how many geohash cells we need to cover the radius
    lat_cells = max(1, int(radius_meters / (lat_error * 111000)))  # 111000m per degree lat
    lng_cells = max(1, int(radius_meters / (lng_error * 111000 * math.cos(math.radians(center_lat)))))
    
    bounds = []
    
    # Generate bounds by expanding around the center geohash
    for lat_offset in range(-lat_cells, lat_cells + 1):
        for lng_offset in range(-lng_cells, lng_cells + 1):
            # Calculate offset coordinates
            offset_lat = center_lat + (lat_offset * lat_error)
            offset_lng = center_lng + (lng_offset * lng_error)
            
            # Check if this offset is within the radius
            distance = calculate_distance(center_lat, center_lng, offset_lat, offset_lng)
            if distance <= radius_meters:
                # Generate geohash for this offset
                offset_geohash = encode_geohash(offset_lat, offset_lng, precision)
                
                # Add bounds for this geohash
                bounds.append({
                    "startHash": offset_geohash,
                    "endHash": offset_geohash + "~"  # ~ is the last character in base32
                })
    
    # Remove duplicates and sort
    unique_bounds = []
    seen = set()
    for bound in bounds:
        key = (bound["startHash"], bound["endHash"])
        if key not in seen:
            seen.add(key)
            unique_bounds.append(bound)
    
    return unique_bounds


def query_events_by_radius(
    db, 
    center_lat: float, 
    center_lng: float, 
    radius_meters: float,
    collection_name: str = "events"
) -> list:
    """
    Query events within a specified radius using geohash bounds.
    
    This function implements the Firebase geohash query pattern to efficiently
    find events within a circular area, then filters out false positives.
    
    Args:
        db: Firestore client instance
        center_lat: Center latitude
        center_lng: Center longitude
        radius_meters: Search radius in meters
        collection_name: Name of the Firestore collection to query
        
    Returns:
        List of event documents within the specified radius
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from typing import List, Dict, Any
    
    # Get geohash query bounds
    bounds = get_geohash_query_bounds(center_lat, center_lng, radius_meters)
    
    if not bounds:
        return []
    
    # Execute queries for each bound
    all_docs = []
    
    def execute_query(bound: Dict[str, str]) -> List[Any]:
        """Execute a single geohash range query."""
        try:
            query = (db.collection(collection_name)
                    .where("geohash", ">=", bound["startHash"])
                    .where("geohash", "<=", bound["endHash"]))
            
            docs = list(query.stream())
            return docs
        except Exception as e:
            print(f"Error executing query for bound {bound}: {e}")
            return []
    
    # Execute all queries in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_bound = {executor.submit(execute_query, bound): bound for bound in bounds}
        
        for future in as_completed(future_to_bound.keys()):
            docs = future.result()
            all_docs.extend(docs)
    
    # Filter out false positives by calculating actual distance
    matching_events = []
    
    for doc in all_docs:
        try:
            data = doc.to_dict()
            
            # Extract coordinates from the document
            position = data.get("position")
            if not position:
                continue
                
            # Handle different position formats
            if hasattr(position, 'latitude') and hasattr(position, 'longitude'):
                # Firebase GeoPoint object
                event_lat = position.latitude
                event_lng = position.longitude
            elif isinstance(position, dict):
                # Dictionary with lat/lng or latitude/longitude keys
                event_lat = position.get('latitude') or position.get('lat')
                event_lng = position.get('longitude') or position.get('lng')
            else:
                continue
                
            if event_lat is None or event_lng is None:
                continue
            
            # Calculate actual distance
            distance = calculate_distance(center_lat, center_lng, event_lat, event_lng)
            
            # Only include if within radius
            if distance <= radius_meters:
                # Add distance to the document data for convenience
                doc_data = data.copy()
                doc_data['_distance_meters'] = round(distance, 2)
                doc_data['_doc_id'] = doc.id
                
                # Convert Firestore data types to JSON-serializable format
                doc_data = _convert_firestore_to_json_serializable(doc_data)
                matching_events.append(doc_data)
                
        except Exception as e:
            print(f"Error processing document {doc.id}: {e}")
            continue
    
    # Sort by distance (closest first)
    matching_events.sort(key=lambda x: x.get('_distance_meters', float('inf')))
    
    return matching_events
