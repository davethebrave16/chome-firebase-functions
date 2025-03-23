from firebase_functions import https_fn

from google.cloud import firestore
from google.cloud.firestore_v1.document import DocumentReference
from firebase_admin import storage
from urllib.parse import urlparse, unquote
import os, uuid

def duplicate_event_associations(old_event_ref: DocumentReference, new_event_ref: DocumentReference) -> https_fn.Response:
    if old_event_ref is None or new_event_ref is None:
        return https_fn.Response("Missing informations refs", 400)
    
    print('Trying to duplicate event associations')
    
    db = firestore.Client()
    if not old_event_ref.get().exists:
        return https_fn.Response("Old event not found", 404)
    if not new_event_ref.get().exists:
        return https_fn.Response("New event not found", 404)
    print('Old event found: ' + old_event_ref.id + ' with title ' + old_event_ref.get().to_dict()["name"])
    print('New event found: ' + new_event_ref.id + ' with title ' + new_event_ref.get().to_dict()["name"])
    old_questions = list(db.collection("event_survey_question").where("event", "==", old_event_ref).stream())
    print('Questions found:', len(old_questions))

    for question in old_questions:
        data = question.to_dict()
        print('Duplicating question: ' + question.id + ' with text ' + data["questionText"])
        data["event"] = new_event_ref
        question_ref = db.collection("event_survey_question").document()
        question_ref.set(data)
        if question_ref.get().exists:
            print('Question duplicated with id ' + question_ref.id)
        else:
            print('Question not duplicated')

    old_medias = list(db.collection("event_media").where("event", "==", old_event_ref).stream())
    print('Medias found:', len(old_medias))

    for media in old_medias:
        data = media.to_dict()
        print('Duplicating media: ' + media.id + ' with path ' + data["path"])
        new_media_path = duplicate_media(data["path"])
        if new_media_path is None:
            print('Error duplicating media. ' + media.id + ' Passing to next one...')
            continue
        data["path"] = new_media_path
        data["event"] = new_event_ref
        media_ref = db.collection("event_media").document()
        media_ref.set(data)
        if media_ref.get().exists:
            print('Media duplicated with id ' + media_ref.id)
        else:
            print('Media not duplicated')
        

    return https_fn.Response("OK", 200)

def delete_event_associations(event_ref, event_data) -> https_fn.Response:
    if event_ref is None:
        return https_fn.Response("Missing event ref", 400)
    print ('Triggered deleting event associations from ' + event_ref.id + ' with title ' + event_data["name"])

    db = firestore.Client() 

    questions = list(db.collection("event_survey_question").where("event", "==", event_ref).stream())
    print('Questions found:', len(questions))
    for question in questions:
        print('Deleting question: ' + question.id + ' with text ' + question.to_dict()["questionText"])
        question_ref = question.reference
        question_ref.delete()
        if not question_ref.get().exists:
            print('Question deleted')
        else:
            print('Question not deleted')

    medias = list(db.collection("event_media").where("event", "==", event_ref).stream())
    print('Medias found:', len(medias))
    for media in medias:
        print('Deleting media: ' + media.id + ' with path ' + media.to_dict()["path"])
        if delete_media(media.to_dict()["path"]):
            print('Media deleted')
        else:
            print('Media not deleted. Passing to next one...')
        media_ref = media.reference
        media_ref.delete()
        if not media_ref.get().exists:
            print('Event media deleted')
        else:
            print('Event media not deleted')

    return https_fn.Response("OK", 200)

def duplicate_media(path: str) -> str:
    bucket = storage.bucket()
    print('Public path ' + path)
    bucket_path = extract_file_path(path)
    print('Bucket path ' + bucket_path)
    folder_path = extract_folder_path(bucket_path)
    print('Folder path ' + folder_path)

    new_file_path = folder_path + '/duplicated/' + uuid.uuid4().hex + '/' + extract_filename(bucket_path)
    try:
        blob = bucket.blob(bucket_path)
        file_contents = blob.download_as_bytes()
        new_blob = bucket.blob(new_file_path)
        new_blob.upload_from_string(file_contents)
        new_url = new_blob.generate_signed_url(expiration=3600 * 24 * 7 * 30 * 12 * 50)  # 50 years
    except Exception as e:
        print("Error duplicating media: " + str(e))
        return None
        
    print ("Media duplicated with url " + new_url)

    return new_url

def delete_media(path: str) -> bool:
    bucket = storage.bucket()
    print('Public path ' + path)
    bucket_path = extract_file_path(path)
    print('Bucket path ' + bucket_path)
    try:
        blob = bucket.blob(bucket_path)
        blob.delete()
        return True
    except Exception as e:
        print("Error deleting media: " + str(e))
        return False

def extract_file_path(url):
    parsed_url = urlparse(url)
    path_with_encoded_slashes = parsed_url.path.split('/o/')[1]
    file_path = unquote(path_with_encoded_slashes)

    return file_path.split('?')[0]

def extract_folder_path(file_path):
    folder_path = os.path.dirname(file_path)
    return folder_path

def extract_filename(file_path):
    filename = os.path.basename(file_path)
    return filename