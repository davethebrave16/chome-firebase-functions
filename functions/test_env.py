#!/usr/bin/env python3
"""Test script to verify environment variables are loaded correctly."""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from chome_functions.config.settings import settings
    
    print("Environment variables loaded:")
    print(f"SECRET: {'✓' if settings.secret else '✗'}")
    print(f"GCP_PROJECT_ID: {'✓' if settings.gcp_project_id else '✗'}")
    print(f"TASK_QUEUE_REGION: {'✓' if settings.task_queue_region else '✗'}")
    print(f"TASK_QUEUE_NAME: {'✓' if settings.task_queue_name else '✗'}")
    print(f"RESERVATION_EXP_CHECK_URL: {'✓' if settings.reservation_exp_check_url else '✗'}")
    print(f"BREVO_SMTP_API_KEY: {'✓' if settings.brevo_smtp_api_key else '✗'}")
    print(f"BREVO_SMTP_BASE_URL: {'✓' if settings.brevo_smtp_base_url else '✗'}")
    
    print("\nTrying to validate settings...")
    try:
        settings.validate()
        print("✓ Settings validation passed!")
    except ValueError as e:
        print(f"✗ Settings validation failed: {e}")
        
except Exception as e:
    print(f"Error loading settings: {e}")
    import traceback
    traceback.print_exc()
