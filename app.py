import flask
import os
from flask import Flask
from flask import jsonify, json
from flask import Response
from flask import request

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import exceptions
from firebase_admin import tenant_mgt

import traceback
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime

# format the log entries
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

# TimeRotatingHandler to auto save log file with the date
if not os.path.exists("Logs/"):
    os.makedirs("Logs/")
handler = TimedRotatingFileHandler('Logs/authentication.log', when='midnight',backupCount=20)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


app = Flask(__name__)
# Firebase service account key file
cred = credentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)

@app.route('/testapi', methods=['GET','POST'])
def test_api():
    return jsonify([{'message':"Test Check", "statusCode":200}])

## Verify the user id
@app.route('/adminLogin', methods=['POST'])
def verify_token_uid():
    try:
        authRequestData = json.loads(request.data)
        # [START verify_token_uid]
        # id_token comes from the client app (shown above)
        decoded_token = auth.verify_id_token(authRequestData['idToken'])
        uid = decoded_token['uid']
        # [END verify_token_uid]

        logger.info("User was successfully authenticated %s" %(uid))
        return jsonify([{'message':"Successfully authenticated user", "statusCode":200}])
    
    except auth.RevokedIdTokenError:
        # Token revoked, inform the user to reauthenticate or signOut().
        logger.exception("Token revoked, inform the user to reauthenticate or signOut().")
        return jsonify([{"message":"Token revoked, Please reauthenticate or signOut()","statusCode":400}])
        pass

    except auth.UserDisabledError:
        # Token belongs to a disabled user record.
        logger.exception("Token belongs to a disabled user record")
        logger.exception(traceback.format_exc())
        return jsonify([{"message":"Your accout is disabled. Please contact support","statusCode":400}])
        pass

    except auth.InvalidIdTokenError:
        # Token is invalid
        logger.exception("Token is invalid")
        logger.exception(traceback.format_exc())
        return jsonify([{"message":"Invalid token, please SignOut and try again","statusCode":400}])
        pass

    except Exception as e:
        logger.info("Wasn't able to authenticate User")
        logger.exception(traceback.format_exc())
        print(traceback.format_exc())
        return jsonify([{"message":"Failed to authenticate","statusCode":400}])


# Sesssion Cookies for all api authentication
session_cookie_expires_in = datetime.timedelta(days=7)
@app.route('/sessionLogin', methods=['POST'])
def session_login():
    # Get the ID token sent by the client
    id_token = request.json['idToken']
    # Set session expiration to 5 days.
    try:
        # Create the session cookie. This will also verify the ID token in the process.
        # The session cookie will have the same claims as the ID token.
        session_cookie = auth.create_session_cookie(id_token, expires_in=session_cookie_expires_in)
        response = jsonify({'message': 'Successfully authenticated user','statusCode':200})
        # Set cookie policy for session cookie.
        expires = datetime.datetime.now() + session_cookie_expires_in
        response.set_cookie('session', session_cookie, expires=expires)
        logger.info("User was successfully authenticated & cookies were generated")
        return response
    except exceptions.FirebaseError:
        return flask.abort(401, 'Failed to create a session cookie')
        pass
    except Exception as e:
        logger.info("Wasn't able to authenticate user and failed to create a session cookie")
        logger.exception(traceback.format_exc())
        print(traceback.format_exc())
        return flask.abort(401, 'Failed to create a session cookie')
        #return jsonify([{"message":"Failed to authenticate","statusCode":400}])


def fetch_profiles():
    """
    :accepts:
    - n =  no. of profiles
    - radius = radius of search
    - current location of user
    - id token
    :process:
    - verify id token
    - get all users uid (Will be refined for querying within a particular radius)
    - filter and sort based on Recommendation Engine
    - eliminate user uids present in current user's Likes and Dislikes
    - pick n top uids from rest of the uids
    :return:
    - array of n uids
    """
    return



if __name__ == '__main__':
    app.run(debug=True)
