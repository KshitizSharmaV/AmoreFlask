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

## Authentication function
# Create a user
def create_user():
    # [START create_user]
    user = auth.create_user(
        email='user@example.com',
        email_verified=False,
        phone_number='+15555550100',
        password='secretPassword',
        display_name='John Doe',
        photo_url='http://www.example.com/12345678/photo.png',
        disabled=False)
    print('Sucessfully created new user: {0}'.format(user.uid))
    # [END create_user]
    return user.uid

## Authentication function
# Create a user in autentication api 
def create_user_with_id():
    # [START create_user_with_id]
    user = auth.create_user(
        uid='some-uid', email='user@example.com', phone_number='+15555550100')
    print('Sucessfully created new user: {0}'.format(user.uid))
    # [END create_user_with_id]    

## Authentication function
# List All Users
def list_all_users():
    # [START list_all_users]
    # Start listing users from the beginning, 1`000 at a time.
    page = auth.list_users()
    while page:
        for user in page.users:
            print('User: ' + user.uid)
        # Get next batch of users.
        page = page.get_next_page()

    # Iterate through all users. This will still retrieve users in batches,
    # buffering no more than 1000 users in memory at a time.
    for user in auth.list_users().iterate_all():
        print('User: ' + user.uid)
    # [END list_all_users]

# Get user by uid
def get_user(uid):
    # [START get_user]
    from firebase_admin import auth

    user = auth.get_user(uid)
    print('Successfully fetched user data: {0}'.format(user.uid))
    print(user)
    # [END get_user]

## Firebase function
def get_firebase_users():
    profile_ref = db.collection(u'Profiles')
    docs = profile_ref.stream()
    for doc in docs:
        print(f'{doc.id} => {doc.to_dict()}')


if __name__ == '__main__':
    
    ## Firebase Auth
    #list_all_users()
    #get_user("sCZ7nWrH1uR4QfAGj6Ndz4Cp3Vv2")

    ## Firebasestore Services
    get_firebase_users()
    







