import asyncio
import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore import AsyncClient

cred = credentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)
# db = firestore.client(app = app)
async_db = AsyncClient(credentials=default_app.credential.get_credential(), project=default_app.project_id)
# Instance of firestore db
db = firestore.client()