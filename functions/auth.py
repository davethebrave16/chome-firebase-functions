import os

from firebase_functions import https_fn

SECRET = os.environ.get('SECRET')

def verify_token(req: https_fn.Request) -> bool:
    token = req.headers.get("Authorization")
    return token == SECRET
