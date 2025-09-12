"""Email service module for Chome Firebase Functions."""

from .email_service import EmailService, send_reservation_confirmation_email

__all__ = ["EmailService", "send_reservation_confirmation_email"]
