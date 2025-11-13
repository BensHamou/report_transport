import firebase_admin
from firebase_admin import credentials
import os

# FIREBASE_CRED_JSON = os.environ.get('FIREBASE_CRED_JSON')
FIREBASE_CRED_JSON = "C:\\Users\\benslimane_m\\Downloads\\firebase-credentials.json"

def init_firebase():
    if firebase_admin._apps:
        return
    if FIREBASE_CRED_JSON and os.path.exists(FIREBASE_CRED_JSON):
        cred = credentials.Certificate(FIREBASE_CRED_JSON)
    else:
        # If you put the JSON content into an env var:
        import json, tempfile
        data = os.environ.get('FIREBASE_CRED_JSON_CONTENT')
        if not data:
            raise RuntimeError("No firebase credentials found")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        tmp.write(data.encode())
        tmp.flush()
        cred = credentials.Certificate(tmp.name)
    firebase_admin.initialize_app(cred)