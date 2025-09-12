"""Main Firebase Functions module for Chome."""

from firebase_functions import https_fn
from firebase_functions.firestore_fn import (
    on_document_deleted,
    on_document_created,
    on_document_updated,
    Event,
    DocumentSnapshot,
    Change,
)
from firebase_admin import initialize_app

from .config.settings import settings
from .utils.app_logging import get_logger
from .auth import verify_token
from .events import duplicate_event_associations, delete_event_associations, process_event_position, search_events_by_radius
from .reservations import (
    send_reservation_confirmation,
    check_reservation_expiration,
    schedule_reservation_expiration_check,
)

# Initialize Firebase app
app = initialize_app()

# Get logger
logger = get_logger(__name__)


# Validate settings on startup
try:
    settings.validate()
    logger.info("Settings validated successfully")
except ValueError as e:
    logger.error(f"Settings validation failed: {str(e)}")
    raise


@on_document_updated(document='event_reservation/{res_id}', region=settings.region)
def on_reservation_confirmed(event: Event[Change[DocumentSnapshot]]) -> https_fn.Response:
    """
    Triggered when a reservation is updated.
    Sends confirmation email if reservation is confirmed.
    """
    try:
        # Get the before and after document snapshots
        before_snapshot = event.data.before
        after_snapshot = event.data.after
        
        if not after_snapshot:
            logger.error("Missing after document snapshot")
            return https_fn.Response("Missing after document snapshot", 400)
        
        doc_ref = after_snapshot.reference
        if not doc_ref:
            logger.error("Missing document reference")
            return https_fn.Response("Missing document reference", 400)
        
        # Get the before and after data to detect the change
        before_data = before_snapshot.to_dict() if before_snapshot else {}
        after_data = after_snapshot.to_dict() if after_snapshot else {}
        
        # Check if confirmed field changed from false/undefined to true
        before_confirmed = before_data.get("confirmed", False)
        after_confirmed = after_data.get("confirmed", False)
        
        # Only trigger if confirmed changed from false/undefined to true
        if not before_confirmed and after_confirmed:
            logger.info(f"Reservation {doc_ref.id} confirmed (changed from {before_confirmed} to {after_confirmed})")
            return send_reservation_confirmation(doc_ref.id)
        else:
            logger.info(f"Reservation {doc_ref.id} - confirmed field: {before_confirmed} -> {after_confirmed}, no action needed")
            return https_fn.Response("No confirmation change detected", 200)
            
    except Exception as e:
        logger.error(f"Error in on_reservation_confirmed: {str(e)}")
        return https_fn.Response(f"Internal server error: {str(e)}", 500)


@on_document_created(document='event/{event_id}', region=settings.region)
def on_event_created(event: Event[DocumentSnapshot | None]) -> https_fn.Response:
    """
    Triggered when a new event is created.
    Duplicates event associations if the event is a duplicate.
    """
    try:
        doc_ref = event.data.reference
        if not doc_ref:
            logger.error("Missing event reference")
            return https_fn.Response("Missing event reference", 400)
        
        doc_data = event.data.to_dict()
        if not doc_data:
            logger.error("Missing event data")
            return https_fn.Response("Missing event data", 400)
        
        event_name = doc_data.get("name", "Unknown")
        logger.info(f"Event created: {doc_ref.id} with title '{event_name}'")
        
        # Process geohash for all events (including duplicates)
        position = doc_data.get("position")
        process_event_position(doc_ref, position, doc_ref.id, "new event")
        
        # Check if this is a duplicate event
        if "duplicateFrom" in doc_data and doc_data["duplicateFrom"] is not None:
            logger.info("Event duplication detected")
            return duplicate_event_associations(doc_data["duplicateFrom"], doc_ref)
        
        logger.info("Event creation processing completed")
        return https_fn.Response("Event created successfully", 200)
        
    except Exception as e:
        logger.error(f"Error in on_event_created: {str(e)}")
        return https_fn.Response(f"Internal server error: {str(e)}", 500)


@on_document_deleted(document='event/{event_id}', region=settings.region)
def on_event_delete(event: Event[DocumentSnapshot | None]) -> https_fn.Response:
    """
    Triggered when an event is deleted.
    Deletes all associated questions and media.
    """
    try:
        doc_ref = event.data.reference
        if not doc_ref:
            logger.error("Missing event reference")
            return https_fn.Response("Missing event reference", 400)
        
        doc_data = event.data.to_dict()
        if not doc_data:
            logger.error("Missing event data")
            return https_fn.Response("Missing event data", 400)
        
        return delete_event_associations(doc_ref, doc_data)
        
    except Exception as e:
        logger.error(f"Error in on_event_delete: {str(e)}")
        return https_fn.Response(f"Internal server error: {str(e)}", 500)


@https_fn.on_request(region=settings.region)
def verify_reservation_expiration(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP endpoint to verify reservation expiration.
    Requires authentication.
    """
    try:
        # Verify authentication
        if not verify_token(req):
            logger.warning("Unauthorized request to verify_reservation_expiration")
            return https_fn.Response("Unauthorized", 401)
        
        res_id = req.args.get("res_id")
        if not res_id:
            logger.error("Missing res_id parameter")
            return https_fn.Response("Missing res_id parameter", 400)
        
        logger.info(f"Checking reservation expiration for: {res_id}")
        return check_reservation_expiration(res_id)
        
    except Exception as e:
        logger.error(f"Error in verify_reservation_expiration: {str(e)}")
        return https_fn.Response(f"Internal server error: {str(e)}", 500)


@on_document_created(document='event_reservation/{res_id}', region=settings.region)
def on_reservation_created(event: Event[DocumentSnapshot | None]) -> https_fn.Response:
    """
    Triggered when a new reservation is created.
    Schedules expiration check for the reservation.
    """
    try:
        doc_ref = event.data.reference
        if not doc_ref:
            logger.error("Missing reservation reference")
            return https_fn.Response("Missing reservation reference", 400)
        
        doc_data = event.data.to_dict()
        if not doc_data:
            logger.error("Missing reservation data")
            return https_fn.Response("Missing reservation data", 400)
        
        logger.info(f"Reservation created: {doc_ref.id}")
        logger.info(f"Event reference: {doc_data.get('event', 'No event reference')}")
        logger.info(f"User reference: {doc_data.get('user', 'No user reference')}")
        
        return schedule_reservation_expiration_check(doc_ref.id)
        
    except Exception as e:
        logger.error(f"Error in on_reservation_created: {str(e)}")
        return https_fn.Response(f"Internal server error: {str(e)}", 500)


@on_document_created(document='user/{user_id}', region=settings.region)
def on_user_created(event: Event[DocumentSnapshot | None]) -> https_fn.Response:
    """
    Triggered when a new user is created.
    Ensures user has proper name fields (firstName, lastName, display_name).
    """
    try:
        doc_ref = event.data.reference
        if not doc_ref:
            logger.error("Missing user document reference")
            return https_fn.Response("Missing user document reference", 400)
        
        doc_data = event.data.to_dict()
        if not doc_data:
            logger.error("Missing user document data")
            return https_fn.Response("Missing user document data", 400)
        
        logger.info(f"User created: {doc_ref.id}")
        logger.info(f"User data: {doc_data}")
        
        # Get current field values
        display_name = doc_data.get('display_name')
        first_name = doc_data.get('firstName')
        last_name = doc_data.get('lastName')
        
        updates = {}
        
        # Case 1: display_name is present but firstName/lastName are not
        if display_name and not first_name and not last_name:
            logger.info(f"Creating firstName and lastName from display_name: {display_name}")
            name_parts = display_name.strip().split(' ', 1)  # Split on first space only
            
            if len(name_parts) >= 2:
                updates['firstName'] = name_parts[0].strip()
                updates['lastName'] = name_parts[1].strip()
                logger.info(f"Split into firstName: '{updates['firstName']}', lastName: '{updates['lastName']}'")
            else:
                # Single name, use as firstName
                updates['firstName'] = name_parts[0].strip()
                logger.info(f"Single name, using as firstName: '{updates['firstName']}'")
        
        # Case 2: firstName and lastName are present but display_name is not
        elif first_name and last_name and not display_name:
            logger.info(f"Creating display_name from firstName and lastName: {first_name} {last_name}")
            updates['display_name'] = f"{first_name.strip()} {last_name.strip()}"
            logger.info(f"Created display_name: '{updates['display_name']}'")
        
        # Case 3: All fields are present, no action needed
        elif display_name and first_name and last_name:
            logger.info("All name fields are present, no updates needed")
            return https_fn.Response("User name fields are complete", 200)
        
        # Case 4: No name fields present, no action possible
        elif not display_name and not first_name and not last_name:
            logger.info("No name fields present, cannot create missing fields")
            return https_fn.Response("No name fields present", 200)
        
        # Apply updates if any
        if updates:
            try:
                doc_ref.update(updates)
                logger.info(f"Successfully updated user {doc_ref.id} with: {updates}")
                return https_fn.Response(f"User updated with: {updates}", 200)
            except Exception as e:
                error_msg = f"Error updating user {doc_ref.id}: {str(e)}"
                logger.error(error_msg)
                return https_fn.Response(error_msg, 500)
        
        return https_fn.Response("No updates needed", 200)
        
    except Exception as e:
        logger.error(f"Error in on_user_created: {str(e)}")
        return https_fn.Response(f"Internal server error: {str(e)}", 500)


@https_fn.on_request(region=settings.region)
def search_events_nearby(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP endpoint to search for events within a specified radius.
    Requires authentication.
    
    Query parameters:
    - lat: Center latitude (-90 to 90)
    - lng: Center longitude (-180 to 180)
    - radius: Search radius in meters (required)
    - collection: Optional collection name (defaults to 'events')
    """
    try:
        # Verify authentication
        if not verify_token(req):
            logger.warning("Unauthorized request to search_events_nearby")
            return https_fn.Response("Unauthorized", 401)
        
        # Get query parameters
        lat_str = req.args.get("lat")
        lng_str = req.args.get("lng")
        radius_str = req.args.get("radius")
        collection_name = req.args.get("collection", "events")
        
        # Validate required parameters
        if not lat_str:
            return https_fn.Response("Missing required parameter: lat", 400)
        if not lng_str:
            return https_fn.Response("Missing required parameter: lng", 400)
        if not radius_str:
            return https_fn.Response("Missing required parameter: radius", 400)
        
        # Parse and validate parameters
        try:
            center_lat = float(lat_str)
            center_lng = float(lng_str)
            radius_meters = float(radius_str)
        except ValueError as e:
            return https_fn.Response(f"Invalid parameter format: {str(e)}", 400)
        
        logger.info(f"Searching events within {radius_meters}m of ({center_lat}, {center_lng})")
        
        # Search for events
        return search_events_by_radius(center_lat, center_lng, radius_meters, collection_name)
        
    except Exception as e:
        logger.error(f"Error in search_events_nearby: {str(e)}")
        return https_fn.Response(f"Internal server error: {str(e)}", 500)


@on_document_updated(document='event/{event_id}', region=settings.region)
def on_event_position_updated(event: Event[Change[DocumentSnapshot]]) -> https_fn.Response:
    """
    Triggered when an event document is updated.
    Updates geohash field if position coordinates have changed.
    """
    try:
        # Get the before and after document snapshots
        before_snapshot = event.data.before
        after_snapshot = event.data.after
        
        if not after_snapshot:
            logger.error("Missing after document snapshot")
            return https_fn.Response("Missing after document snapshot", 400)
        
        doc_ref = after_snapshot.reference
        if not doc_ref:
            logger.error("Missing document reference")
            return https_fn.Response("Missing document reference", 400)
        
        # Get the before and after data to detect position changes
        before_data = before_snapshot.to_dict() if before_snapshot else {}
        after_data = after_snapshot.to_dict() if after_snapshot else {}
        
        # Check if position field has changed
        before_position = before_data.get("position")
        after_position = after_data.get("position")
        
        # Check if position has changed
        if before_position == after_position:
            logger.info(f"Event {doc_ref.id} position unchanged, skipping geohash update")
            return https_fn.Response("Position unchanged", 200)
        
        # Process geohash if position exists and has changed
        if process_event_position(doc_ref, after_position, doc_ref.id, "event update"):
            return https_fn.Response("Geohash updated successfully", 200)
        else:
            return https_fn.Response("No position field found or invalid position", 200)
            
    except Exception as e:
        logger.error(f"Error in on_event_position_updated: {str(e)}")
        return https_fn.Response(f"Internal server error: {str(e)}", 500)
