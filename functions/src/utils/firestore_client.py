"""Firestore client utilities."""

from google.cloud import firestore
from typing import Optional

# Global Firestore client instance
_firestore_client: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """Get or create a Firestore client instance."""
    global _firestore_client
    if _firestore_client is None:
        _firestore_client = firestore.Client()
    return _firestore_client
