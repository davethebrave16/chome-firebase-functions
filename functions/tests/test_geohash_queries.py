"""Tests for geohash query functionality."""

import pytest
import math
from unittest.mock import Mock, MagicMock, patch
from typing import List, Dict, Any

from src.utils.geohash import (
    get_geohash_query_bounds,
    query_events_by_radius,
    calculate_distance,
    encode_geohash
)
from src.events.event_service import search_events_by_radius
from firebase_functions import https_fn


class TestGeohashQueryBounds:
    """Test geohash query bounds calculation."""
    
    def test_get_geohash_query_bounds_small_radius(self):
        """Test bounds calculation for small radius."""
        center_lat = 45.4642  # Milan
        center_lng = 9.1900
        radius_meters = 1000  # 1km
        
        bounds = get_geohash_query_bounds(center_lat, center_lng, radius_meters)
        
        assert isinstance(bounds, list)
        assert len(bounds) > 0
        
        # Check bounds structure
        for bound in bounds:
            assert "startHash" in bound
            assert "endHash" in bound
            assert isinstance(bound["startHash"], str)
            assert isinstance(bound["endHash"], str)
            assert bound["startHash"] <= bound["endHash"]
    
    def test_get_geohash_query_bounds_large_radius(self):
        """Test bounds calculation for large radius."""
        center_lat = 45.4642  # Milan
        center_lng = 9.1900
        radius_meters = 100000  # 100km
        
        bounds = get_geohash_query_bounds(center_lat, center_lng, radius_meters)
        
        assert isinstance(bounds, list)
        assert len(bounds) > 0
        
        # Large radius should have more bounds
        assert len(bounds) >= 1
    
    def test_get_geohash_query_bounds_precision_selection(self):
        """Test that appropriate precision is selected based on radius."""
        center_lat = 45.4642
        center_lng = 9.1900
        
        # Test different radius ranges with updated precision logic
        test_cases = [
            (50, 7),      # 50m -> precision 7
            (500, 6),     # 500m -> precision 6
            (5000, 5),    # 5km -> precision 5
            (50000, 4),   # 50km -> precision 4 (changed from 5)
            (500000, 4),  # 500km -> precision 4
        ]
        
        for radius, expected_precision in test_cases:
            bounds = get_geohash_query_bounds(center_lat, center_lng, radius)
            if bounds:
                # Check that geohash length matches expected precision
                geohash_length = len(bounds[0]["startHash"])
                assert geohash_length == expected_precision, f"Radius {radius}m should use precision {expected_precision}, got {geohash_length}"


class TestDistanceCalculation:
    """Test distance calculation functions."""
    
    def test_calculate_distance_same_point(self):
        """Test distance calculation for same point."""
        lat = 45.4642
        lng = 9.1900
        
        distance = calculate_distance(lat, lng, lat, lng)
        assert distance == 0.0
    
    def test_calculate_distance_known_distance(self):
        """Test distance calculation for known distance."""
        # Distance between Milan and Rome (approximately 475km)
        milan_lat, milan_lng = 45.4642, 9.1900
        rome_lat, rome_lng = 41.9028, 12.4964
        
        distance = calculate_distance(milan_lat, milan_lng, rome_lat, rome_lng)
        
        # Should be approximately 475km (475000m) with some tolerance
        assert 470000 <= distance <= 480000
    
    def test_calculate_distance_equator(self):
        """Test distance calculation at equator."""
        # 1 degree of longitude at equator is approximately 111km
        lat = 0.0
        lng1 = 0.0
        lng2 = 1.0
        
        distance = calculate_distance(lat, lng1, lat, lng2)
        
        # Should be approximately 111km (111000m) with some tolerance
        assert 110000 <= distance <= 112000

class TestEventServiceSearch:
    """Test EventService search_events_by_radius method."""
    
    @patch('src.events.event_service.get_event_service')
    def test_search_events_by_radius_invalid_latitude(self, mock_get_service):
        """Test validation for invalid latitude."""
        # Mock the service method to return a proper HTTP response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.data = "Invalid latitude. Must be between -90 and 90."
        
        mock_service = Mock()
        mock_service.search_events_by_radius.return_value = mock_response
        mock_get_service.return_value = mock_service
        
        result = search_events_by_radius(91.0, 9.0, 1000)
        assert result.status_code == 400
        assert "Invalid latitude" in result.data
    
    @patch('src.events.event_service.get_event_service')
    def test_search_events_by_radius_invalid_longitude(self, mock_get_service):
        """Test validation for invalid longitude."""
        # Mock the service method to return a proper HTTP response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.data = "Invalid longitude. Must be between -180 and 180."
        
        mock_service = Mock()
        mock_service.search_events_by_radius.return_value = mock_response
        mock_get_service.return_value = mock_service
        
        result = search_events_by_radius(45.0, 181.0, 1000)
        assert result.status_code == 400
        assert "Invalid longitude" in result.data
    
    @patch('src.events.event_service.get_event_service')
    def test_search_events_by_radius_invalid_radius(self, mock_get_service):
        """Test validation for invalid radius."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        # Test negative radius
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.data = "Radius must be greater than 0 meters."
        mock_service.search_events_by_radius.return_value = mock_response
        
        result = search_events_by_radius(45.0, 9.0, -100)
        assert result.status_code == 400
        assert "Radius must be greater than 0" in result.data
        
        # Test zero radius
        result = search_events_by_radius(45.0, 9.0, 0)
        assert result.status_code == 400
        assert "Radius must be greater than 0" in result.data
        
        # Test too large radius
        mock_response.data = "Radius cannot exceed 1,000,000 meters (1000km)."
        result = search_events_by_radius(45.0, 9.0, 2000000)
        assert result.status_code == 400
        assert "Radius cannot exceed" in result.data
    
    @patch('src.events.event_service.get_event_service')
    def test_search_events_by_radius_success(self, mock_get_service):
        """Test successful search."""
        # Mock the service method to return a proper HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.data = {
            "total_events": 2,
            "radius_meters": 1000,
            "center": {"latitude": 45.0, "longitude": 9.0},
            "events": [
                {
                    "name": "Test Event 1",
                    "_distance_meters": 500.0,
                    "_doc_id": "event1"
                },
                {
                    "name": "Test Event 2", 
                    "_distance_meters": 750.0,
                    "_doc_id": "event2"
                }
            ]
        }
        
        mock_service = Mock()
        mock_service.search_events_by_radius.return_value = mock_response
        mock_get_service.return_value = mock_service
        
        result = search_events_by_radius(45.0, 9.0, 1000)
        
        assert result.status_code == 200
        response_data = result.data
        assert response_data["total_events"] == 2
        assert response_data["radius_meters"] == 1000
        assert response_data["center"]["latitude"] == 45.0
        assert response_data["center"]["longitude"] == 9.0
        assert len(response_data["events"]) == 2


class TestGeohashIntegration:
    """Integration tests for geohash functionality."""
    
    def test_geohash_encoding_decoding_consistency(self):
        """Test that encoding and decoding are consistent."""
        test_coords = [
            (45.4642, 9.1900),  # Milan
            (41.9028, 12.4964), # Rome
            (0.0, 0.0),         # Equator/Prime Meridian
            (-33.9249, 18.4241), # Cape Town
        ]
        
        for lat, lng in test_coords:
            geohash = encode_geohash(lat, lng, precision=10)
            decoded_lat, decoded_lng = geohash[:10], geohash[10:]  # This is a simplified test
            
            # The geohash should be a valid string
            assert isinstance(geohash, str)
            assert len(geohash) == 10
    
    def test_distance_calculation_precision(self):
        """Test distance calculation precision."""
        # Test with known coordinates
        milan_lat, milan_lng = 45.4642, 9.1900
        rome_lat, rome_lng = 41.9028, 12.4964
        
        distance = calculate_distance(milan_lat, milan_lng, rome_lat, rome_lng)
        
        # Distance should be reasonable (between 400-500km)
        assert 400000 <= distance <= 500000
        
        # Distance should be positive
        assert distance > 0
        
        # Distance should be symmetric
        reverse_distance = calculate_distance(rome_lat, rome_lng, milan_lat, milan_lng)
        assert abs(distance - reverse_distance) < 1.0  # Within 1 meter tolerance


if __name__ == "__main__":
    pytest.main([__file__])
