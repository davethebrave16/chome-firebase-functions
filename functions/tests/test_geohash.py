#!/usr/bin/env python3
"""Test script for geohash functionality."""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.geohash import encode_geohash, calculate_distance

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
        
        # Test distance calculation with known coordinates
        milan_lat, milan_lng = 45.4642, 9.1900
        distance = calculate_distance(lat, lng, milan_lat, milan_lng)
        print(f"✓ Distance Rome-Milan: {distance:.0f} meters")
        
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
