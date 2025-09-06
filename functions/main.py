"""Main entry point for Firebase Functions."""

# Load environment variables from .env file before importing modules
import os
from dotenv import load_dotenv

# Load .env file if it exists
if os.path.exists('.env'):
    load_dotenv()
    print("Environment variables loaded from .env file")

# Import all functions from the main module
from src.chome_functions.main import (
    on_reservation_confirmed,
    on_event_created,
    on_event_delete,
    verify_reservation_expiration,
    on_reservation_created,
    on_user_created,
)

# Re-export all functions for Firebase Functions
__all__ = [
    "on_reservation_confirmed",
    "on_event_created", 
    "on_event_delete",
    "verify_reservation_expiration",
    "on_reservation_created",
    "on_user_created",
]