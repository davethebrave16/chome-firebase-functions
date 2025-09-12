#!/usr/bin/env python3
"""Test script for geohash functionality."""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.geohash import encode_geohash, decode_geohash, get_geohash_center, calculate_distance

def test_geohash_functions():
    """Test the geohash utility functions."""
    print("Testing geohash functions...")
    
    # Test coordinates (Rome, Italy)
    lat = 41.9028
    lng = 12.4964
    
    try:
        # Test encoding
        geohash = encode_geohash(lat, lng, precision=10)
        print(f"✓ Encoded ({lat}, {lng}) to geohash: {geohash}")
        
        # Test decoding
        lat_min, lat_max, lng_min, lng_max = decode_geohash(geohash)
        print(f"✓ Decoded geohash bounds: lat({lat_min:.6f}, {lat_max:.6f}), lng({lng_min:.6f}, {lng_max:.6f})")
        
        # Test center point
        center_lat, center_lng = get_geohash_center(geohash)
        print(f"✓ Geohash center: ({center_lat:.6f}, {center_lng:.6f})")
        
        # Test distance calculation
        distance = calculate_distance(lat, lng, center_lat, center_lng)
        print(f"✓ Distance from original to center: {distance:.2f} meters")
        
        # Test with different precision
        geohash_short = encode_geohash(lat, lng, precision=5)
        print(f"✓ Short geohash (precision 5): {geohash_short}")
        
        print("\n✅ All geohash tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_geohash_functions()
    sys.exit(0 if success else 1)
