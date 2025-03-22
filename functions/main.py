# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_functions.firestore_fn import (
  on_document_deleted,
  on_document_created,
  on_document_updated,
  Event,
  Change,
  DocumentSnapshot,
)
from firebase_admin import initialize_app
from google.cloud import firestore
from reservations import send_reservation_confirmation
from events import duplicate_event_associations, delete_event_associations
from auth import verify_token

app = initialize_app()

region = 'europe-west1'

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
            doc_data["duplicateFrom"] = db.collection("event").document("XzqGBxWFyiXUGoFpcS2u").get().reference'
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

@on_document_updated(document='event_reservation/{reservation_id}', region=region)
def on_reservation_update(event: Event[Change[DocumentSnapshot]]) -> https_fn.Response:
    doc_ref = event.data.after.reference
    doc_data_before = event.data.before.to_dict()
    doc_data_after = event.data.after.to_dict()
    print ("Reservation updated " + doc_ref.id)
    if ("confirmed" not in doc_data_before or doc_data_before["confirmed"] == False or doc_data_before["confirmed"] is None) and ("confirmed" in doc_data_after and doc_data_after["confirmed"] == True):
        return send_reservation_confirmation(doc_ref)
    print ("No actions done!")
    return https_fn.Response("No actions done!", 204)