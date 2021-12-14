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
from firebase_admin import firestore

import traceback
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import string
import random

from fetchprofiles import FetchProfiles

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
session_cookie_expires_in = datetime.timedelta(days=7)

# Instance of firestore db
db = firestore.client()
# Instances for fetchprofiles
fetchProfilesObj = FetchProfiles(db=db, logger=logger)


@app.route('/testapi', methods=['GET','POST'])
def test_api():
    return jsonify([{'message':"Test Check", "statusCode":200}])


# Sesssion Cookies for all api authentication
# Once the user has logged in on the app from the firebase : Client side authentication
# We call session_login for server side authentication
# The function accepts idToken which is generated on client side & create a session cookie for it
# The sesssion cookie is sent back and then used further by client side for communicating with APIs
# Session cookie is validated before every api call
# The session cookie is valid for 7 days, if expired do another call from client side to sessionLogin
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




# fetch_profiles is used to get profiles for cards in swipe view
@app.route('/fetchprofiles', methods=['POST'])
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
    session_cookie = flask.request.cookies.get('session')
    if not session_cookie:
        # Session cookie is unavailable. Force user to login.
        logger.info("Failed to authenticate in fetch_profiles, no session cookie found")
        logger.exception(traceback.format_exc())
        return flask.abort(401, 'No session cookie available')
    # Verify the session cookie. In this case an additional check is added to detect
    # if the user's Firebase session was revoked, user deleted/disabled, etc.
    try:
        decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
        profilesArray = fetchProfilesObj.getProfiles(userId=decoded_claims['user_id'],
                                                    idsAlreadyInDeck= request.json["idsAlreadyInDeck"])
        return jsonify(profilesArray)
    except auth.InvalidSessionCookieError:
        logger.info("Failed to authenticate in fetch_profiles, not a valid session cookie")
        logger.exception(traceback.format_exc())
        # Session cookie is invalid, expired or revoked. Force user to login.
        return flask.abort(401, 'Failed to authenticate, not a valid session cookie')
    return flask.abort(400, 'An error occured in API')



# fetch_likes_given is used to get profiles which are super liked by the user
@app.route('/fetchlikesgiven', methods=['POST'])
def fetch_likes_given():
    """
    :accepts:
    just the reponse cookie and we decode the user id then get profiles superliked by the user
    """
    session_cookie = flask.request.cookies.get('session')
    if not session_cookie:
        # Session cookie is unavailable. Force user to login.
        logger.info("Failed to authenticate in fetch_profiles, no session cookie found")
        logger.exception(traceback.format_exc())
        return flask.abort(401, 'No session cookie available')
    # Verify the session cookie. In this case an additional check is added to detect
    # if the user's Firebase session was revoked, user deleted/disabled, etc.
    try:
        decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
        superLikedIdsList = fetchProfilesObj.superLikedProfilesByUser(userId = decoded_claims['user_id'])
        profilesArray = fetchProfilesObj.getProfilesForListOfIds(listofIds=superLikedIdsList)
        return jsonify(profilesArray)
    except auth.InvalidSessionCookieError:
        logger.info("Failed to authenticate in fetch_profiles, not a valid session cookie")
        logger.exception(traceback.format_exc())
        # Session cookie is invalid, expired or revoked. Force user to login.
        return flask.abort(401, 'Failed to authenticate, not a valid session cookie')
    return flask.abort(400, 'An error occured in API')
 


if __name__ == '__main__':
    app.run(debug=True)