"""Tests for authentication module."""

import pytest
from unittest.mock import Mock, patch
from src.chome_functions.auth import verify_token


class TestAuth:
    """Test cases for authentication functionality."""
    
    @patch('src.chome_functions.auth.settings')
    def test_verify_token_valid(self, mock_settings):
        """Test token verification with valid token."""
        mock_settings.secret = "test_secret"
        
        # Mock request with valid token
        mock_request = Mock()
        mock_request.headers.get.return_value = "test_secret"
        
        result = verify_token(mock_request)
        assert result is True
    
    @patch('src.chome_functions.auth.settings')
    def test_verify_token_invalid(self, mock_settings):
        """Test token verification with invalid token."""
        mock_settings.secret = "test_secret"
        
        # Mock request with invalid token
        mock_request = Mock()
        mock_request.headers.get.return_value = "wrong_secret"
        
        result = verify_token(mock_request)
        assert result is False
    
    @patch('src.chome_functions.auth.settings')
    def test_verify_token_missing(self, mock_settings):
        """Test token verification with missing token."""
        mock_settings.secret = "test_secret"
        
        # Mock request with no token
        mock_request = Mock()
        mock_request.headers.get.return_value = None
        
        result = verify_token(mock_request)
        assert result is False
