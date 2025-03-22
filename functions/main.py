# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn, firestore_fn
from firebase_admin import initialize_app
from reservations import send_reservation_confirmation
from events import test_delete_event_associations, duplicate_event_associations
from auth import verify_token

app = initialize_app()

region = 'europe-west1'

@https_fn.on_request(region=region)
def on_complete_reservation(req: https_fn.Request) -> https_fn.Response:
    res_id = req.args.get("res_id")
    return send_reservation_confirmation()

@https_fn.on_request(region=region)
def on_event_duplicate(req: https_fn.Request) -> https_fn.Response:
    if not verify_token(req):
        return https_fn.Response("Unauthorized", 401)
    new_event_id = req.args.get("new_event_id")
    old_event_id = req.args.get("old_event_id")
    return duplicate_event_associations(new_event_id, old_event_id)

@firestore_fn.on_document_deleted(document='event/{event_id}', region=region)
def on_event_delete_trigger(event_id: str) -> https_fn.Response:
    return test_delete_event_associations(event_id)

@https_fn.on_request(region=region)
def on_event_delete(req: https_fn.Request) -> https_fn.Response:
    if not verify_token(req):
        return https_fn.Response("Unauthorized", 401)
    event_id = req.args.get("event_id")
    return test_delete_event_associations(event_id)