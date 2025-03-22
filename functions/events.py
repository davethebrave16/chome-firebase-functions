from firebase_functions import https_fn
from google.cloud import firestore

def duplicate_event_associations(new_event_id: str, old_event_id: str) -> https_fn.Response:
    if old_event_id is None or new_event_id is None:
        return https_fn.Response("Missing informations ids", 400)
    
    print('Trying to duplicate event associations from ' + old_event_id + ' to ' + new_event_id)
    
    db = firestore.Client()
    old_event_ref = db.collection("event").document(old_event_id)
    if not old_event_ref.get().exists:
        return https_fn.Response("Old event not found", 404)
    new_event_ref = db.collection("event").document(new_event_id)
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

    return https_fn.Response("OK", 200)
