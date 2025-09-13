"""HTTP response utilities for Firebase Functions."""

import json
from firebase_functions import https_fn
from typing import Any, Dict, Optional


def json_response(data: Any, status_code: int = 200) -> https_fn.Response:
    """
    Create a JSON HTTP response with proper content-type header.
    
    Args:
        data: Data to serialize as JSON (dict, list, or any JSON-serializable object)
        status_code: HTTP status code (default: 200)
        
    Returns:
        Firebase Functions HTTP response with JSON content
    """
    return https_fn.Response(
        json.dumps(data), 
        status_code, 
        headers={"Content-Type": "application/json"}
    )


def json_error_response(message: str, status_code: int = 400) -> https_fn.Response:
    """
    Create a JSON error response with proper content-type header.
    
    Args:
        message: Error message
        status_code: HTTP status code (default: 400)
        
    Returns:
        Firebase Functions HTTP response with JSON error content
    """
    return json_response({"error": message}, status_code)


def json_success_response(data: Any, status_code: int = 200) -> https_fn.Response:
    """
    Create a JSON success response with proper content-type header.
    
    Args:
        data: Data to serialize as JSON
        status_code: HTTP status code (default: 200)
        
    Returns:
        Firebase Functions HTTP response with JSON content
    """
    return json_response(data, status_code)
