"""Reservation service for handling reservation-related operations."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from firebase_functions import https_fn
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from sqlite3.dbapi2 import Timestamp

from ..config.settings import settings
from ..utils.firestore_client import get_firestore_client
from ..utils.app_logging import get_logger
from ..email.email_service import send_reservation_confirmation_email

logger = get_logger(__name__)


class ReservationService:
    """Service for handling reservation-related operations."""
    
    def __init__(self):
        """Initialize the reservation service."""
        self.db = get_firestore_client()
        self.tasks_client = tasks_v2.CloudTasksClient()
    
    def send_reservation_confirmation(self, res_id: str) -> https_fn.Response:
        """
        Send reservation confirmation email.
        
        Args:
            res_id: Reservation ID
            
        Returns:
            HTTP response indicating success or failure
        """
        if not res_id:
            logger.error("Missing reservation ID")
            return https_fn.Response("Missing reservation ID", 400)
        
        try:
            logger.info(f"Processing reservation confirmation for ID: {res_id}")
            
            # Get reservation document
            doc_ref = self.db.collection("event_reservation").document(res_id)
            res_doc = doc_ref.get()
            
            if not res_doc.exists:
                logger.error(f"Reservation {res_id} not found")
                return https_fn.Response("Reservation not found", 404)
            
            res_data = res_doc.to_dict()
            
            # Get user data
            user_data = self._get_user_data(res_data.get("user"))
            if not user_data:
                logger.error(f"User not found for reservation {res_id}")
                return https_fn.Response("User not found", 404)
            
            # Get event data
            event_data = self._get_event_data(res_data.get("event"))
            
            # Prepare reservation data for email
            reservation_data = {
                "id": res_id,
                "name": res_data.get("name", "Reservation"),
                "createdAt": res_data.get("createdAt"),
                "confirmed": res_data.get("confirmed", False)
            }
            
            # Send confirmation email
            email_result = send_reservation_confirmation_email(
                user_email=user_data.get("email"),
                user_name=user_data.get("display_name", "User"),
                reservation_data=reservation_data,
                event_data=event_data
            )
            
            if email_result.get("success"):
                logger.info(f"Reservation confirmation email sent successfully to {user_data.get('email')}")
                return https_fn.Response("Reservation confirmation email sent", 200)
            else:
                logger.error(f"Failed to send email: {email_result.get('error')}")
                return https_fn.Response("Email service error", 500)
                
        except Exception as e:
            error_msg = f"Error sending reservation confirmation email: {str(e)}"
            logger.error(error_msg)
            return https_fn.Response(error_msg, 500)
    
    def check_reservation_expiration(self, reservation_id: str) -> https_fn.Response:
        """
        Check if a reservation has expired and delete it if necessary.
        
        Args:
            reservation_id: Reservation ID to check
            
        Returns:
            HTTP response indicating the result
        """
        if not reservation_id:
            logger.error("Missing reservation ID")
            return https_fn.Response("Missing reservation ID", 400)
        
        try:
            logger.info(f"Checking expiration for reservation: {reservation_id}")
            
            doc_ref = self.db.collection("event_reservation").document(reservation_id)
            res_doc = doc_ref.get()
            
            if not res_doc.exists:
                logger.warning(f"Reservation {reservation_id} not found")
                return https_fn.Response("Reservation not found", 404)
            
            res_data = res_doc.to_dict()
            
            # Check if already confirmed
            if res_data.get("confirmed") is True:
                logger.info(f"Reservation {reservation_id} already confirmed")
                return https_fn.Response("Reservation already confirmed", 200)
            
            # Check if createdAt exists
            if "createdAt" not in res_data:
                logger.warning(f"Reservation {reservation_id} has no createdAt field, deleting")
                doc_ref.delete()
                return https_fn.Response("Reservation deleted", 200)
            
            # Check expiration
            res_timestamp = res_data.get("createdAt").timestamp()
            current_timestamp = Timestamp.now().timestamp()
            
            if current_timestamp - res_timestamp > settings.reservation_exp_time:
                logger.info(f"Reservation {reservation_id} expired, deleting")
                doc_ref.delete()
                return https_fn.Response("Reservation deleted", 200)
            
            logger.info(f"Reservation {reservation_id} still valid")
            return https_fn.Response("Reservation still valid", 200)
            
        except Exception as e:
            error_msg = f"Error checking reservation expiration: {str(e)}"
            logger.error(error_msg)
            return https_fn.Response(error_msg, 500)
    
    def schedule_reservation_expiration_check(self, res_id: str) -> https_fn.Response:
        """
        Schedule a task to check reservation expiration.
        
        Args:
            res_id: Reservation ID to schedule check for
            
        Returns:
            HTTP response indicating success or failure
        """
        if not res_id:
            logger.error("Missing reservation ID")
            return https_fn.Response("Missing reservation ID", 400)
        
        try:
            logger.info(f"Scheduling expiration check for reservation: {res_id}")
            
            # Verify reservation exists
            doc_ref = self.db.collection("event_reservation").document(res_id)
            res_doc = doc_ref.get()
            
            if not res_doc.exists:
                logger.error(f"Reservation {res_id} not found")
                return https_fn.Response("Reservation not found", 404)
            
            # Create Cloud Task
            parent = self.tasks_client.queue_path(
                settings.gcp_project_id,
                settings.task_queue_region,
                settings.task_queue_name
            )
            
            scheduled_time = datetime.now() + timedelta(seconds=settings.task_schedule_delay)
            logger.info(f"Scheduled time: {scheduled_time}")
            
            timestamp = timestamp_pb2.Timestamp()
            timestamp.FromDatetime(scheduled_time)
            
            task = {
                "http_request": {
                    "http_method": "GET",
                    "url": f"{settings.reservation_exp_check_url}?res_id={res_id}",
                    "headers": {
                        "Authorization": settings.secret
                    }
                },
                "schedule_time": timestamp
            }
            
            response = self.tasks_client.create_task(request={"parent": parent, "task": task})
            
            if response.name:
                logger.info(f"Created task: {response.name}")
                return https_fn.Response("Task scheduled successfully", 200)
            else:
                logger.error("Task not created")
                return https_fn.Response("Failed to create task", 500)
                
        except Exception as e:
            error_msg = f"Error scheduling reservation expiration check: {str(e)}"
            logger.error(error_msg)
            return https_fn.Response(error_msg, 500)
    
    def _get_user_data(self, user_ref) -> Optional[Dict[str, Any]]:
        """Get user data from user reference."""
        if not user_ref:
            return None
        
        try:
            if hasattr(user_ref, 'get'):
                # It's a document reference
                user_doc = user_ref.get()
            else:
                # It's a string ID, get the document
                user_doc = self.db.collection("user").document(str(user_ref)).get()
            
            if user_doc.exists:
                return user_doc.to_dict()
            else:
                logger.warning("User document does not exist")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user data: {str(e)}")
            return None
    
    def _get_event_data(self, event_ref) -> Dict[str, Any]:
        """Get event data from event reference."""
        if not event_ref:
            return {}
        
        try:
            if isinstance(event_ref, str):
                # Clean the event_ref - remove any path separators and get just the ID
                event_id = event_ref.strip()
                if '/' in event_id:
                    event_id = event_id.split('/')[-1]
                
                if event_id and event_id.strip():
                    event_doc_ref = self.db.collection("event").document(event_id)
                    event_doc = event_doc_ref.get()
                    if event_doc.exists:
                        return event_doc.to_dict()
                    else:
                        logger.warning(f"Event document {event_id} does not exist")
                else:
                    logger.warning(f"Invalid event ID: '{event_id}'")
            
            elif hasattr(event_ref, 'get'):
                # It's a document reference
                event_doc = event_ref.get()
                if event_doc.exists:
                    return event_doc.to_dict()
                else:
                    logger.warning("Event document reference does not exist")
            else:
                logger.warning(f"Unexpected event reference type: {type(event_ref)}")
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting event data: {str(e)}")
            return {}


# Global reservation service instance
_reservation_service: Optional[ReservationService] = None


def get_reservation_service() -> ReservationService:
    """Get or create the reservation service instance."""
    global _reservation_service
    if _reservation_service is None:
        _reservation_service = ReservationService()
    return _reservation_service


def send_reservation_confirmation(res_id: str) -> https_fn.Response:
    """
    Convenience function to send reservation confirmation.
    
    Args:
        res_id: Reservation ID
        
    Returns:
        HTTP response indicating success or failure
    """
    try:
        reservation_service = get_reservation_service()
        return reservation_service.send_reservation_confirmation(res_id)
    except Exception as e:
        logger.error(f"Error in send_reservation_confirmation: {str(e)}")
        return https_fn.Response(f"Error sending reservation confirmation: {str(e)}", 500)


def check_reservation_expiration(reservation_id: str) -> https_fn.Response:
    """
    Convenience function to check reservation expiration.
    
    Args:
        reservation_id: Reservation ID to check
        
    Returns:
        HTTP response indicating the result
    """
    try:
        reservation_service = get_reservation_service()
        return reservation_service.check_reservation_expiration(reservation_id)
    except Exception as e:
        logger.error(f"Error in check_reservation_expiration: {str(e)}")
        return https_fn.Response(f"Error checking reservation expiration: {str(e)}", 500)


def schedule_reservation_expiration_check(res_id: str) -> https_fn.Response:
    """
    Convenience function to schedule reservation expiration check.
    
    Args:
        res_id: Reservation ID to schedule check for
        
    Returns:
        HTTP response indicating success or failure
    """
    try:
        reservation_service = get_reservation_service()
        return reservation_service.schedule_reservation_expiration_check(res_id)
    except Exception as e:
        logger.error(f"Error in schedule_reservation_expiration_check: {str(e)}")
        return https_fn.Response(f"Error scheduling reservation expiration check: {str(e)}", 500)
