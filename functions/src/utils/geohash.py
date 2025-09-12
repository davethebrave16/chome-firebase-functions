"""Geohash utility functions for location-based queries."""

import math
from typing import Tuple


def encode_geohash(latitude: float, longitude: float, precision: int = 10) -> str:
    """
    Encode latitude and longitude into a geohash string.
    
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
    
    # Base32 alphabet used in geohash
    base32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    
    # Initialize bounds
    lat_min, lat_max = -90.0, 90.0
    lng_min, lng_max = -180.0, 180.0
    
    geohash = ""
    bit = 0
    ch = 0
    even = True
    
    while len(geohash) < precision:
        if even:
            # Longitude
            mid = (lng_min + lng_max) / 2
            if longitude >= mid:
                ch |= (1 << (4 - bit))
                lng_min = mid
            else:
                lng_max = mid
        else:
            # Latitude
            mid = (lat_min + lat_max) / 2
            if latitude >= mid:
                ch |= (1 << (4 - bit))
                lat_min = mid
            else:
                lat_max = mid
        
        even = not even
        bit += 1
        
        if bit == 5:
            geohash += base32[ch]
            bit = 0
            ch = 0
    
    return geohash


def decode_geohash(geohash: str) -> Tuple[float, float, float, float]:
    """
    Decode a geohash string to latitude and longitude bounds.
    
    Args:
        geohash: Geohash string to decode
        
    Returns:
        Tuple of (latitude_min, latitude_max, longitude_min, longitude_max)
        
    Raises:
        ValueError: If geohash contains invalid characters
    """
    if not geohash:
        raise ValueError("Geohash cannot be empty")
    
    # Base32 alphabet used in geohash
    base32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    
    # Initialize bounds
    lat_min, lat_max = -90.0, 90.0
    lng_min, lng_max = -180.0, 180.0
    
    even = True
    
    for char in geohash.lower():
        if char not in base32:
            raise ValueError(f"Invalid character '{char}' in geohash")
        
        char_index = base32.index(char)
        
        for i in range(5):
            bit = (char_index >> (4 - i)) & 1
            
            if even:
                # Longitude
                mid = (lng_min + lng_max) / 2
                if bit:
                    lng_min = mid
                else:
                    lng_max = mid
            else:
                # Latitude
                mid = (lat_min + lat_max) / 2
                if bit:
                    lat_min = mid
                else:
                    lat_max = mid
            
            even = not even
    
    return lat_min, lat_max, lng_min, lng_max


def get_geohash_center(geohash: str) -> Tuple[float, float]:
    """
    Get the center point of a geohash.
    
    Args:
        geohash: Geohash string
        
    Returns:
        Tuple of (latitude, longitude) representing the center
    """
    lat_min, lat_max, lng_min, lng_max = decode_geohash(geohash)
    return (lat_min + lat_max) / 2, (lng_min + lng_max) / 2


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
    
    This is a simplified implementation. For production use, consider using
    a more sophisticated library like geohash2 or pygeohash.
    
    Args:
        center_lat: Center latitude
        center_lng: Center longitude
        radius_meters: Search radius in meters
        
    Returns:
        List of geohash bounds for querying
    """
    # Approximate precision based on radius
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
    
    # For simplicity, return a single bound
    # In production, you'd want to calculate multiple bounds to cover the circle
    return [{"startHash": center_geohash, "endHash": center_geohash + "~"}]
