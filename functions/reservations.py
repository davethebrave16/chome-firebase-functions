import os
from sqlite3.dbapi2 import Timestamp
from firebase_functions import https_fn
from google.cloud import firestore
from google.cloud import tasks_v2
from google.cloud.firestore_v1.document import DocumentReference
from google.protobuf import timestamp_pb2
from datetime import datetime, timedelta


def send_reservation_confirmation(res_id: str) -> https_fn.Response:
    print(res_id)
    if res_id is None:
        return https_fn.Response("Missing res id", 400)
    
    db = firestore.Client()
    doc_ref = db.collection("event_reservation").document(res_id)
    res_doc = doc_ref.get()
    if not res_doc.exists:
        return https_fn.Response("Reservation not found", 404)
    
    user_ref = res_doc.to_dict().get("user")
    if user_ref is None:
        return https_fn.Response("User not found", 404)
    
    user_doc = user_ref.get()
    if not user_doc.exists:
        return https_fn.Response("User not found", 404)
    
    user_data = user_doc.to_dict()
    print(user_data)

    return https_fn.Response("OK", 200)

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
    
    print ("Trying to schedule reservation expiration check for " + res_id + " with title " + res_doc.to_dict()["name"])
    
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