import os
from sqlite3.dbapi2 import Timestamp
from firebase_functions import https_fn
from google.cloud import firestore
from google.cloud import tasks_v2
from google.cloud.firestore_v1.document import DocumentReference
from google.protobuf import timestamp_pb2
from datetime import datetime, timedelta
from email_service import send_reservation_confirmation_email


def send_reservation_confirmation(res_id: str) -> https_fn.Response:
    print(f"Processing reservation confirmation for ID: {res_id}")
    if res_id is None:
        return https_fn.Response("Missing res id", 400)
    
    db = firestore.Client()
    doc_ref = db.collection("event_reservation").document(res_id)
    res_doc = doc_ref.get()
    if not res_doc.exists:
        return https_fn.Response("Reservation not found", 404)
    
    res_data = res_doc.to_dict()
    user_ref = res_data.get("user")
    if user_ref is None:
        return https_fn.Response("User not found", 404)
    
    user_doc = user_ref.get()
    if not user_doc.exists:
        return https_fn.Response("User not found", 404)
    
    user_data = user_doc.to_dict()
    print(f"User data: {user_data}")
    
    # Get event data if available
    event_ref = res_data.get("event")
    event_data = {}
    if event_ref:
        print(f"Event reference: {event_ref} (type: {type(event_ref)})")
        
        # If event_ref is a string (event ID), construct the document reference
        if isinstance(event_ref, str):
            # Clean the event_ref - remove any path separators and get just the ID
            event_id = event_ref.strip()
            if '/' in event_id:
                # If it's a full path like "event/abc123", extract just the ID
                event_id = event_id.split('/')[-1]
                print(f"Extracted event ID from path: {event_id}")
            
            # Validate that the ID is not empty
            if event_id and event_id.strip():
                try:
                    event_doc_ref = db.collection("event").document(event_id)
                    event_doc = event_doc_ref.get()
                    if event_doc.exists:
                        event_data = event_doc.to_dict()
                        print(f"Event data: {event_data}")
                    else:
                        print(f"Event document {event_id} does not exist")
                except Exception as e:
                    print(f"Error accessing event document {event_id}: {str(e)}")
            else:
                print(f"Invalid event ID: '{event_id}'")
        # If event_ref is already a document reference
        elif hasattr(event_ref, 'get'):
            try:
                event_doc = event_ref.get()
                if event_doc.exists:
                    event_data = event_doc.to_dict()
                    print(f"Event data: {event_data}")
                else:
                    print("Event document reference does not exist")
            except Exception as e:
                print(f"Error accessing event document reference: {str(e)}")
        else:
            print(f"Unexpected event reference type: {type(event_ref)}")
    
    # Prepare reservation data for email
    reservation_data = {
        "id": res_id,
        "name": res_data.get("name", "Reservation"),
        "createdAt": res_data.get("createdAt"),
        "confirmed": res_data.get("confirmed", False)
    }
    
    # Send confirmation email
    try:
        email_result = send_reservation_confirmation_email(
            user_email=user_data.get("email"),
            user_name=user_data.get("display_name", "User"),
            reservation_data=reservation_data,
            event_data=event_data
        )
        
        if email_result.get("success"):
            print(f"Reservation confirmation email sent successfully to {user_data.get('email')}")
            return https_fn.Response("Reservation confirmation email sent", 200)
        else:
            print(f"Failed to send email: {email_result.get('error')}")
            return https_fn.Response("Email service error", 500)
            
    except Exception as e:
        error_msg = f"Error sending reservation confirmation email: {str(e)}"
        print(error_msg)
        return https_fn.Response(error_msg, 500)

def check_reservation_expiration(reservation_id: str) -> https_fn.Response:
    db = firestore.Client()
    doc_ref = db.collection("event_reservation").document(reservation_id)
    res_doc = doc_ref.get()
    if not res_doc.exists:
        print ("Reservation " + reservation_id + " not found")
        return https_fn.Response("Reservation not found", 404)
    
    res_data = res_doc.to_dict()
    
    if res_data.get("confirmed") is True:
        print ("Reservation " + reservation_id + " already confirmed")
        return https_fn.Response("Reservation already confirmed", 200)
    
    if "createdAt" not in res_data:
        print ("Reservation " + reservation_id + " created at not found. Deleting...")
        doc_ref.delete()
        return https_fn.Response("Reservation deleted", 200)
    
    print ("Reservation " + reservation_id + " created at: " + str(res_data.get("createdAt")))
    res_timestamp = res_data.get("createdAt").timestamp()
    current_timestamp = Timestamp.now().timestamp()

    res_exp_time = os.environ.get("RESERVATION_EXP_TIME")
    if current_timestamp - res_timestamp > int(res_exp_time):
        print ("Reservation " + reservation_id + " expired. Deleting...")
        doc_ref.delete()
        return https_fn.Response("Reservation deleted", 200)

    
    return https_fn.Response("Reservation still valid", 200)

def schedule_reservation_expiration_check(res_id: str) -> https_fn.Response:
    if res_id is None:
        return https_fn.Response("Missing res id", 400)
    
    db = firestore.Client()
    doc_ref = db.collection("event_reservation").document(res_id)
    res_doc = doc_ref.get()
    if not res_doc.exists:
        return https_fn.Response("Reservation not found", 404)
    
    print ("Trying to schedule reservation expiration check for " + res_id)
    
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path(os.environ.get("GCP_PROJECT_ID"), os.environ.get("TASK_QUEUE_REGION"), os.environ.get("TASK_QUEUE_NAME"))
    exp_check_url = os.environ.get("RESERVATION_EXP_CHECK_URL")
    exp_check_token = os.environ.get("SECRET")

    scheduler_after = os.environ.get("TASK_SCHEDULE_DELAY")
    
    scheduled_time = datetime.now() + timedelta(seconds=int(scheduler_after))
    print("Scheduled time: " + str(scheduled_time))

    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(scheduled_time)

    task = {
        "http_request": {
            "http_method": "GET",
            "url": exp_check_url + "?res_id=" + res_id,
            "headers": {
                "Authorization": exp_check_token
            }
        },
        "schedule_time": timestamp
    }

    try:
        response = client.create_task(request={"parent": parent, "task": task})
        if response.name:
            print("Created task " + response.name)
        else:
            print("Task not created")
    except Exception as e:
        print("Exception while creating task: " + str(e))
    return https_fn.Response("OK", 200)