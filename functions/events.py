from firebase_functions import https_fn
from google.cloud import firestore

def duplicate_event_associations(new_event_id: str, old_event_id: str) -> https_fn.Response:
    if old_event_id is None or new_event_id is None:
        return https_fn.Response("Missing informations ids", 400)
    
    print('Trying to duplicate event associations from ' + old_event_id + ' to ' + new_event_id)
    
    db = firestore.Client()
    
    old_questions = db.collection("event_survey_question").where("event", "==", '/event/' + old_event_id).stream()

    print('Questions found: ' + str(len(list(old_questions))))

    for question in old_questions:
        data = question.to_dict()
        print('Duplicating question: ' + data.id + ' with text ' + data["questionText"])
        data["event"] = '/event/' + new_event_id
        question_ref = db.collection("event_survey_question").document()
        question_ref.set(data)
        if question_ref.get().exists:
            print('Question duplicated')
        else:
            print('Question not duplicated')
        

    return https_fn.Response("OK", 200)