import flask
from flask import Flask, jsonify, request
from firebase_admin import auth, exceptions
import traceback
import datetime
import time
from ProjectConf.FirestoreConf import db
from ProjectConf.LoggerConf import logger
from Services.fetchprofiles import getProfiles, get_profiles_within_radius, superLikedProfilesByUser, getProfilesForListOfIds
import geohash2

app = Flask(__name__)

session_cookie_expires_in = datetime.timedelta(days=7)

@app.route('/testapi', methods=['GET', 'POST'])
def test_api():
    return jsonify([{'message': "Test Check", "statusCode": 200}])


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
        response = jsonify({'message': 'Successfully authenticated user', 'statusCode': 200})
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
        # return jsonify([{"message":"Failed to authenticate","statusCode":400}])


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
        profilesArray = getProfiles(userId=decoded_claims['user_id'],
                                                     idsAlreadyInDeck=request.json["idsAlreadyInDeck"])
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
        superLikedIdsList = superLikedProfilesByUser(userId=decoded_claims['user_id'])
        profilesArray = getProfilesForListOfIds(listofIds=superLikedIdsList)
        return jsonify(profilesArray)
    except auth.InvalidSessionCookieError:
        logger.info("Failed to authenticate in fetch_profiles, not a valid session cookie")
        logger.exception(traceback.format_exc())
        # Session cookie is invalid, expired or revoked. Force user to login.
        return flask.abort(401, 'Failed to authenticate, not a valid session cookie')
    return flask.abort(400, 'An error occured in API')


@app.route('/storelikesdislikes', methods=['POST'])
def store_likes_dislikes_superlikes():
    """
    Endpoint to store likes, superlikes, dislikes, liked_by, disliked_by, superliked_by for users
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

        """
        Body of Request contains following payloads:
        - current user id
        - swipe info: Like, Dislike, Superlike
        - swiped profile id
        """
        current_user_id = request.json['currentUserID']
        swipe_info = request.json['swipeInfo']
        swiped_user_id = request.json['swipedUserID']
        db.collection('LikesDislikes').document(current_user_id).collection(swipe_info).document(swiped_user_id).set(
            {"id": swiped_user_id, "timestamp": time.time()})
        by_collection = "LikedBy" if swipe_info == "Likes" else "DislikedBy" if swipe_info == "Dislikes" else "SuperlikedBy"
        db.collection('LikesDislikes').document(swiped_user_id).collection(by_collection).document(current_user_id).set(
            {"id": current_user_id, "timestamp": time.time()})

        return jsonify({'status': 200})
    except auth.InvalidSessionCookieError:
        logger.info("Failed to authenticate in fetch_profiles, not a valid session cookie")
        logger.exception(traceback.format_exc())
        # Session cookie is invalid, expired or revoked. Force user to login.
        return flask.abort(401, 'Failed to authenticate, not a valid session cookie')
    return flask.abort(400, 'An error occured in API')


@app.route('/getgeohash', methods=['POST'])
def get_geohash_for_location():
    """
    Endpoint to get Geohash for given latitude and longitude
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
        """
        Body of Request contains following payloads:
        - latitude
        - longitude
        - precision
        While Updating the Filters and Location, get Geohash for the user location
        """
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        precision = int(request.json['precision'])
        geohash = geohash2.encode(latitude=latitude, longitude=longitude, precision=precision)
        return jsonify({'geohash': geohash})
    except auth.InvalidSessionCookieError:
        logger.info("Failed to authenticate in fetch_profiles, not a valid session cookie")
        logger.exception(traceback.format_exc())
        # Session cookie is invalid, expired or revoked. Force user to login.
        return flask.abort(401, 'Failed to authenticate, not a valid session cookie')
    return flask.abort(400, 'An error occured in API')

# fetch_profiles within given radius for cards in swipe view
@app.route('/fetchprofileswithinradius', methods=['POST'])
def fetch_profiles_within_given_radius():
    """
    :accepts:
    - n =  no. of profiles
    - radius = radius of search
    - Current location of user -- Latitude, Longitude
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
        userId = decoded_claims['user_id']
        idsAlreadyInDeck = request.json["idsAlreadyInDeck"]
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        radius = int(request.json['radius'])
        profilesArray = get_profiles_within_radius(userId=userId, idsAlreadyInDeck=idsAlreadyInDeck, latitude=latitude, longitude=longitude, radius=radius)
        return jsonify(profilesArray)
    except auth.InvalidSessionCookieError:
        logger.info("Failed to authenticate in fetch_profiles, not a valid session cookie")
        logger.exception(traceback.format_exc())
        # Session cookie is invalid, expired or revoked. Force user to login.
        return flask.abort(401, 'Failed to authenticate, not a valid session cookie')
    return flask.abort(400, 'An error occured in API')


# every time a user swipes the application calls this api to store data in collection
@app.route('/reportProfile', methods=['POST']) 
def report_profiles():
    """
    Endpoint to store likes, superlikes, dislikes, liked_by, disliked_by, superliked_by for users
    """
    session_cookie = flask.request.cookies.get('session')
    if not session_cookie:
        logger.info("Failed to authenticate in fetch_profiles, no session cookie found")
        logger.exception(traceback.format_exc())
        return flask.abort(401, 'No session cookie available')
    try:
        decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
        """
        Body of Request contains following payloads:
        - current user id
        - reported profile id
        """
        current_user_id = decoded_claims['user_id']
        reported_profile_id = request.json['swipedProfileID']
        reason_given = request.json['reasonGiven']
        description_given = request.json['descriptionGiven']
        db.collection('ReportedProfile').document(reported_profile_id).collection(current_user_id).document("ReportingDetails").set({"reportedById": current_user_id, 
                                                                        "idBeingReported":reported_profile_id,
                                                                        "reasonGiven":reason_given,
                                                                        "descriptionGiven":description_given,
                                                                        "timestamp": time.time()
                                                                    })
        return jsonify({'status': 200})
    except auth.InvalidSessionCookieError:
        logger.info("Failed to authenticate in fetch_profiles, not a valid session cookie")
        logger.exception(traceback.format_exc())
        return flask.abort(401, 'Failed to authenticate, not a valid session cookie')
    return flask.abort(400, 'An error occured in API')



if __name__ == '__main__':
    app.run(debug=True)
