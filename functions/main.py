"""Main entry point for Firebase Functions."""

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