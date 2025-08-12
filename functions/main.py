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