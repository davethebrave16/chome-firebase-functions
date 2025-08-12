# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

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
from google.cloud import firestore
from reservations import check_reservation_expiration, schedule_reservation_expiration_check, send_reservation_confirmation
from events import duplicate_event_associations, delete_event_associations
from auth import verify_token

app = initialize_app()

region = 'europe-west1'

@on_document_updated(document='event_reservation/{res_id}', region=region)
def on_reservation_confirmed(event: Event[Change[DocumentSnapshot]]) -> https_fn.Response:
    # Get the before and after document snapshots
    before_snapshot = event.data.before
    after_snapshot = event.data.after
    
    if after_snapshot is None:
        return https_fn.Response("Missing after document snapshot", 400)
    
    doc_ref = after_snapshot.reference
    if doc_ref is None:
        return https_fn.Response("Missing document reference", 400)
    
    # Get the before and after data to detect the change
    before_data = before_snapshot.to_dict() if before_snapshot else {}
    after_data = after_snapshot.to_dict() if after_snapshot else {}
    
    # Check if confirmed field changed from false/undefined to true
    before_confirmed = before_data.get("confirmed", False)
    after_confirmed = after_data.get("confirmed", False)
    
    # Only trigger if confirmed changed from false/undefined to true
    if not before_confirmed and after_confirmed:
        print(f"Reservation {doc_ref.id} confirmed (changed from {before_confirmed} to {after_confirmed}), sending confirmation email")
        return send_reservation_confirmation(doc_ref.id)
    else:
        print(f"Reservation {doc_ref.id} - confirmed field: {before_confirmed} -> {after_confirmed}, no action needed")
        return https_fn.Response("No confirmation change detected", 200)

@on_document_created(document='event/{event_id}', region=region)
def on_event_created(event: Event[DocumentSnapshot|None]) -> https_fn.Response:
    doc_ref = event.data.reference
    if doc_ref is None:
        return https_fn.Response("Missing event ref", 400)
    doc_data = event.data.to_dict()
    print ("Event created " + doc_ref.id + " with title " + doc_data["name"])
    if "duplicateFrom" in doc_data and doc_data["duplicateFrom"] is not None:
        '''
        if doc_data["duplicateFrom"] == "":
            print("Event duplication from default")
            db = firestore.Client()
            doc_data["duplicateFrom"] = db.collection("event").document("XnTJDgRrNGa2OOb6kJMD").get().reference
        '''
        print("Event duplication")
        return duplicate_event_associations(doc_data["duplicateFrom"], doc_ref)
    print ("No actions done!")
    return https_fn.Response("No actions done!", 204)

@on_document_deleted(document='event/{event_id}', region=region)
def on_event_delete(event: Event[DocumentSnapshot|None]) -> https_fn.Response:
    doc_ref = event.data.reference
    doc_data = event.data.to_dict()
    return delete_event_associations(doc_ref, doc_data)

@https_fn.on_request(region=region)
def verify_reservation_expiration(req: https_fn.Request) -> https_fn.Response:
    if not verify_token(req):
        return https_fn.Response("Unauthorized", 401)
    res_id = req.args.get("res_id")
    return check_reservation_expiration(res_id)

@on_document_created(document='event_reservation/{res_id}', region=region)
def on_reservation_created(event: Event[DocumentSnapshot|None]) -> https_fn.Response:
    doc_ref = event.data.reference
    doc_data = event.data.to_dict()
    print(f"Reservation created {doc_ref.id}")
    print(f"Event reference: {doc_data.get('event', 'No event reference')}")
    print(f"User reference: {doc_data.get('user', 'No user reference')}")
    return schedule_reservation_expiration_check(doc_ref.id)

@on_document_created(document='user/{user_id}', region=region)
def on_user_created(event: Event[DocumentSnapshot|None]) -> https_fn.Response:
    doc_ref = event.data.reference
    if doc_ref is None:
        return https_fn.Response("Missing user document reference", 400)
    
    doc_data = event.data.to_dict()
    if doc_data is None:
        return https_fn.Response("Missing user document data", 400)
    
    print(f"User created {doc_ref.id}")
    print(f"User data: {doc_data}")
    
    # Get current field values
    display_name = doc_data.get('display_name')
    first_name = doc_data.get('firstName')
    last_name = doc_data.get('lastName')
    
    updates = {}
    
    # Case 1: display_name is present but firstName/lastName are not
    if display_name and not first_name and not last_name:
        print(f"Creating firstName and lastName from display_name: {display_name}")
        name_parts = display_name.strip().split(' ', 1)  # Split on first space only
        
        if len(name_parts) >= 2:
            updates['firstName'] = name_parts[0].strip()
            updates['lastName'] = name_parts[1].strip()
            print(f"Split into firstName: '{updates['firstName']}', lastName: '{updates['lastName']}'")
        else:
            # Single name, use as firstName
            updates['firstName'] = name_parts[0].strip()
            print(f"Single name, using as firstName: '{updates['firstName']}'")
    
    # Case 2: firstName and lastName are present but display_name is not
    elif first_name and last_name and not display_name:
        print(f"Creating display_name from firstName and lastName: {first_name} {last_name}")
        updates['display_name'] = f"{first_name.strip()} {last_name.strip()}"
        print(f"Created display_name: '{updates['display_name']}'")
    
    # Case 3: All fields are present, no action needed
    elif display_name and first_name and last_name:
        print("All name fields are present, no updates needed")
        return https_fn.Response("User name fields are complete", 200)
    
    # Case 4: No name fields present, no action possible
    elif not display_name and not first_name and not last_name:
        print("No name fields present, cannot create missing fields")
        return https_fn.Response("No name fields present", 200)
    
    # Apply updates if any
    if updates:
        try:
            db = firestore.Client()
            doc_ref.update(updates)
            print(f"Successfully updated user {doc_ref.id} with: {updates}")
            return https_fn.Response(f"User updated with: {updates}", 200)
        except Exception as e:
            error_msg = f"Error updating user {doc_ref.id}: {str(e)}"
            print(error_msg)
            return https_fn.Response(error_msg, 500)
    
    return https_fn.Response("No updates needed", 200)