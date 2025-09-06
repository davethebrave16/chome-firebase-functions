#!/usr/bin/env python3
"""Test script to verify Firebase Functions can be imported without errors."""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing Firebase Functions import...")
    
    # Test importing the main module
    from chome_functions.main import (
        on_reservation_confirmed,
        on_event_created,
        on_event_delete,
        verify_reservation_expiration,
        on_reservation_created,
        on_user_created,
    )
    
    print("✓ All Firebase Functions imported successfully!")
    print("Available functions:")
    print("- on_reservation_confirmed")
    print("- on_event_created")
    print("- on_event_delete")
    print("- verify_reservation_expiration")
    print("- on_reservation_created")
    print("- on_user_created")
    
except Exception as e:
    print(f"✗ Error importing Firebase Functions: {e}")
    import traceback
    traceback.print_exc()
