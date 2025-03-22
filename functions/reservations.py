from firebase_functions import https_fn
from google.cloud import firestore
from utils import send_email
from google.cloud.firestore_v1.document import DocumentReference

def send_reservation_confirmation(reservation_ref: DocumentReference) -> https_fn.Response:
    subject = "Conferma della tua prenotazione"
    body = "Grazie per averci contattato, la prenotazione è stata confermata"
    user_ref = reservation_ref.get().to_dict()["user"]
    to_email = user_ref.get().to_dict()["email"]

    send_email(subject, body, to_email)

    return https_fn.Response("OK", 200)