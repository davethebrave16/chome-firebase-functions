"""Email service using Brevo API."""

import os
import requests
from typing import Dict, Optional
from datetime import datetime

from ..config.settings import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """Centralized email service using Brevo API."""
    
    def __init__(self):
        """Initialize the email service with configuration."""
        self.api_key = settings.brevo_smtp_api_key
        self.base_url = settings.brevo_smtp_base_url
        self.sender_email = settings.brevo_smtp_sender_email
        self.sender_name = settings.brevo_smtp_sender_name
        
        if not self.api_key:
            raise ValueError("BREVO_SMTP_API_KEY environment variable is required")
        if not self.base_url:
            raise ValueError("BREVO_SMTP_BASE_URL environment variable is required")
    
    def _format_event_date(self, date_value) -> str:
        """
        Format event date in a user-friendly way.
        
        Args:
            date_value: Date value from Firestore (could be datetime, string, or other)
        
        Returns:
            Formatted date string
        """
        if date_value is None:
            return "Date to be determined"
        
        try:
            # If it's a Firestore DatetimeWithNanoseconds
            if hasattr(date_value, 'strftime'):
                return date_value.strftime("%A, %B %d, %Y at %I:%M %p")
            
            # If it's a string, try to parse it
            elif isinstance(date_value, str):
                return date_value
            
            # If it's a timestamp or other numeric type
            elif hasattr(date_value, 'timestamp'):
                dt = datetime.fromtimestamp(date_value.timestamp())
                return dt.strftime("%A, %B %d, %Y at %I:%M %p")
            
            # Fallback
            else:
                return str(date_value)
                
        except Exception as e:
            logger.error(f"Error formatting date {date_value}: {str(e)}")
            return str(date_value)
    
    def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        template_id: Optional[int] = None,
        template_data: Optional[Dict] = None
    ) -> Dict:
        """
        Send an email using Brevo API.
        
        Args:
            to_email: Recipient email address
            to_name: Recipient name
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            template_id: Brevo template ID (optional)
            template_data: Data for template variables (optional)
        
        Returns:
            Dict containing the API response
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        payload = {
            "sender": {
                "email": self.sender_email,
                "name": self.sender_name
            },
            "to": [
                {
                    "email": to_email,
                    "name": to_name
                }
            ],
            "subject": subject
        }
        
        # Use template if provided, otherwise use direct content
        if template_id and template_data:
            payload["templateId"] = template_id
            payload["params"] = template_data
        else:
            payload["htmlContent"] = html_content
            if text_content:
                payload["textContent"] = text_content
        
        try:
            response = requests.post(
                f"{self.base_url}/smtp/email",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Email sent successfully to {to_email}. Message ID: {result.get('messageId')}")
            return {"success": True, "message_id": result.get("messageId"), "response": result}
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to send email to {to_email}: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": str(e)}
    
    def send_reservation_confirmation_email(
        self,
        user_email: str,
        user_name: str,
        reservation_data: Dict,
        event_data: Dict
    ) -> Dict:
        """
        Send reservation confirmation email.
        
        Args:
            user_email: User's email address
            user_name: User's name
            reservation_data: Reservation information
            event_data: Event information
        
        Returns:
            Dict containing the send result
        """
        subject = f"Reservation Confirmed - {event_data.get('name', 'Event')}"
        
        # Create HTML content for the confirmation email
        html_content = self._create_reservation_confirmation_html(
            user_name, reservation_data, event_data
        )
        
        # Create plain text version
        text_content = self._create_reservation_confirmation_text(
            user_name, reservation_data, event_data
        )
        
        return self.send_email(
            to_email=user_email,
            to_name=user_name,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    def _create_reservation_confirmation_html(
        self,
        user_name: str,
        reservation_data: Dict,
        event_data: Dict
    ) -> str:
        """Create HTML content for reservation confirmation email."""
        event_name = event_data.get('name', 'Event')
        event_date = self._format_event_date(event_data.get('date'))
        event_location = event_data.get('address', 'TBD')
        reservation_id = reservation_data.get('id', 'N/A')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reservation Confirmed</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }}
                .details {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #4CAF50; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Reservation Confirmed!</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{user_name}</strong>,</p>
                    <p>Your reservation has been successfully confirmed. Here are the details:</p>
                    
                    <div class="details">
                        <h3>Event Details</h3>
                        <p><strong>Event:</strong> {event_name}</p>
                        <p><strong>Date:</strong> {event_date}</p>
                        <p><strong>Location:</strong> {event_location}</p>
                        <p><strong>Reservation ID:</strong> {reservation_id}</p>
                    </div>
                    
                    <p>We look forward to seeing you at the event!</p>
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from VisitHome System</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _create_reservation_confirmation_text(
        self,
        user_name: str,
        reservation_data: Dict,
        event_data: Dict
    ) -> str:
        """Create plain text content for reservation confirmation email."""
        event_name = event_data.get('name', 'Event')
        event_date = self._format_event_date(event_data.get('date'))
        event_location = event_data.get('address', 'TBD')
        reservation_id = reservation_data.get('id', 'N/A')
        
        text = f"""
Reservation Confirmed!

Dear {user_name},

Your reservation has been successfully confirmed. Here are the details:

Event Details:
- Event: {event_name}
- Date: {event_date}
- Location: {event_location}
- Reservation ID: {reservation_id}

We look forward to seeing you at the event!

If you have any questions, please don't hesitate to contact us.

---
This is an automated message from Chome System
        """
        return text.strip()


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create the email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


def send_reservation_confirmation_email(
    user_email: str,
    user_name: str,
    reservation_data: Dict,
    event_data: Dict
) -> Dict:
    """
    Convenience function to send reservation confirmation emails.
    
    Args:
        user_email: User's email address
        user_name: User's name
        reservation_data: Reservation information
        event_data: Event information
    
    Returns:
        Dict containing the send result
    """
    try:
        email_service = get_email_service()
        return email_service.send_reservation_confirmation_email(
            user_email=user_email,
            user_name=user_name,
            reservation_data=reservation_data,
            event_data=event_data
        )
    except Exception as e:
        error_msg = f"Reservation confirmation email error: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
