from firebase_functions import https_fn
from google.cloud import firestore

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