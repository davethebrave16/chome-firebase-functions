# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_functions.firestore_fn import (
  on_document_deleted,
  on_document_created,
  Event,
  DocumentSnapshot,
)
from firebase_admin import initialize_app
from google.cloud import firestore
from reservations import check_reservation_expiration, schedule_reservation_expiration_check, send_reservation_confirmation
from events import duplicate_event_associations, delete_event_associations
from auth import verify_token

app = initialize_app()

region = 'europe-west1'

@https_fn.on_request(region=region)
def on_complete_reservation(req: https_fn.Request) -> https_fn.Response:
    res_id = req.args.get("res_id")
    return send_reservation_confirmation()

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
    print ("Reservation created " + doc_ref.id + " with title " + doc_data["name"])
    return schedule_reservation_expiration_check(doc_ref.id)