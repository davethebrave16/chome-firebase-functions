"""Main entry point for Firebase Functions."""

# Load environment variables from .env file before importing modules
import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path so we can import src modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Load .env file if it exists
if os.path.exists('.env'):
    load_dotenv()
    print("Environment variables loaded from .env file")

# Import all functions from the main module
from src.main import (
    on_reservation_confirmed,
    on_event_created,
    on_event_delete,
    on_event_position_updated,
    verify_reservation_expiration,
    on_reservation_created,
    on_user_created,
)

# Re-export all functions for Firebase Functions
__all__ = [
    "on_reservation_confirmed",
    "on_event_created", 
    "on_event_delete",
    "on_event_position_updated",
    "verify_reservation_expiration",
    "on_reservation_created",
    "on_user_created",
]