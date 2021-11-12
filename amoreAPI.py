# [START import_sdk]
import firebase_admin
# [END import_sdk]
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import exceptions
from firebase_admin import tenant_mgt
from firebase_admin import firestore

cred = credentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

## Verify the user id
def verify_token_uid(id_token):
    
    # [START verify_token_uid]
    # id_token comes from the client app (shown above)

    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token['uid']
    # [END verify_token_uid]
    print(uid)
    
