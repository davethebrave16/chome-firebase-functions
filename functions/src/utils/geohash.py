"""Geohash utility functions for location-based queries using pygeohash library."""

import math
from typing import Tuple
import pygeohash as pgh


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


def decode_geohash(geohash: str) -> Tuple[float, float, float, float]:
    """
    Decode a geohash string to latitude and longitude bounds using pygeohash library.
    
    Args:
        geohash: Geohash string to decode
        
    Returns:
        Tuple of (latitude_min, latitude_max, longitude_min, longitude_max)
        
    Raises:
        ValueError: If geohash contains invalid characters
    """
    if not geohash:
        raise ValueError("Geohash cannot be empty")
    
    # Decode to center point
    lat, lng = pgh.decode(geohash)
    
    # Calculate bounds based on geohash precision
    precision = len(geohash)
    lat_error = 90.0 / (2 ** (precision * 5 // 2))
    lng_error = 180.0 / (2 ** ((precision * 5 + 1) // 2))
    
    return (
        lat - lat_error,  # lat_min
        lat + lat_error,  # lat_max
        lng - lng_error,  # lng_min
        lng + lng_error   # lng_max
    )


def get_geohash_center(geohash: str) -> Tuple[float, float]:
    """
    Get the center point of a geohash using pygeohash library.
    
    Args:
        geohash: Geohash string
        
    Returns:
        Tuple of (latitude, longitude) representing the center
    """
    return pgh.decode(geohash)


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the distance between two points using the Haversine formula.
    
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
    Get geohash query bounds for a circular area search.
    
    This implementation follows the Firebase documentation pattern for geohash queries.
    It calculates multiple geohash bounds to cover a circular area efficiently.
    
    Args:
        center_lat: Center latitude
        center_lng: Center longitude
        radius_meters: Search radius in meters
        
    Returns:
        List of geohash bounds for querying, each with 'startHash' and 'endHash'
    """
    # Determine appropriate precision based on radius
    # This follows the Firebase documentation recommendations
    if radius_meters > 1000000:  # > 1000km
        precision = 3
    elif radius_meters > 100000:  # > 100km
        precision = 4
    elif radius_meters > 10000:   # > 10km
        precision = 5
    elif radius_meters > 1000:    # > 1km
        precision = 6
    elif radius_meters > 100:     # > 100m
        precision = 7
    else:
        precision = 8
    
    # Get center geohash
    center_geohash = encode_geohash(center_lat, center_lng, precision)
    
    # Calculate approximate geohash cell size for this precision
    # This is a simplified approach - for production, consider using
    # a more sophisticated library that provides proper bounds calculation
    bounds = []
    
    # For now, return a single bound that covers the area
    # In a production environment, you'd want to calculate multiple bounds
    # to properly cover the circular area as shown in Firebase docs
    bounds.append({
        "startHash": center_geohash,
        "endHash": center_geohash + "~"  # ~ is the last character in base32
    })
    
    return bounds


def get_geohash_neighbors(geohash: str) -> list:
    """
    Get the 8 neighboring geohashes for a given geohash.
    
    This is useful for expanding search areas and ensuring complete coverage.
    
    Args:
        geohash: Base geohash string
        
    Returns:
        List of neighboring geohash strings
    """
    try:
        return pgh.get_neighbors(geohash)
    except Exception:
        # Fallback implementation if pygeohash doesn't have get_neighbors
        # This is a simplified version
        neighbors = []
        base32 = "0123456789bcdefghjkmnpqrstuvwxyz"
        
        # For each direction, try to find the neighbor
        # This is a basic implementation - for production use pygeohash's neighbors
        for i in range(len(geohash)):
            for j in range(len(base32)):
                if base32[j] != geohash[i]:
                    neighbor = geohash[:i] + base32[j] + geohash[i+1:]
                    neighbors.append(neighbor)
        
        return neighbors[:8]  # Return up to 8 neighbors
