import flask
from flask import Flask, jsonify, request
import traceback
import time
import geohash2
import logging

app = Flask(__name__)
from ProjectConf.FirestoreConf import db
from ProjectConf.AuthenticationDecorators import validateCookie
from FlaskHelpers.AsyncioPlugin import run_coroutine

with app.app_context():
    from FlaskHelpers.AppAuthentication import auth_app
    from FlaskHelpers.AppSuperLikesDislikes import app_super_likes_dislikes
    from FlaskHelpers.AppSwipeView import app_swipe_view_app
from FlaskHelpers.FetchProfiles import get_profiles_within_radius
from FlaskHelpers.UnmatchHelper.UnmatchHelper import unmatch_task_function

logging.basicConfig(filename='Logs/app.log', level=logging.DEBUG,
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app.logger.setLevel(logging.INFO)


@app.route('/getgeohash', methods=['POST'])
@validateCookie
def get_geohash_for_location(decoded_claims=None):
    """
    Endpoint to get Geohash for given latitude and longitude
    Body of Request contains following payloads:
    - latitude
    - longitude
    - precision
    While Updating the Filters and Location, get Geohash for the user location
    """
    try:
        userId = decoded_claims['user_id']
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        precision = int(request.json['precision'])
        geohash = geohash2.encode(latitude=latitude, longitude=longitude, precision=precision)
        app.logger.info("%s Successfully got geo hash for location /getgeohash" % (userId))
        return jsonify({'geohash': geohash})
    except Exception as e:
        app.logger.exception("%s Failed to get geo locataion for user in /getgeohash" % (userId))
        app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /getgeohash')


# fetch_profiles within given radius for cards in swipe view
@app.route('/fetchprofileswithinradius', methods=['POST'])
@validateCookie
def fetch_profiles_within_given_radius(decoded_claims=None):
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
    try:
        userId = decoded_claims['user_id']
        idsAlreadyInDeck = request.json["idsAlreadyInDeck"]
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        radius = int(request.json['radius'])
        profilesArray = get_profiles_within_radius(userId=userId, ids_already_in_deck=idsAlreadyInDeck,
                                                   latitude=latitude, longitude=longitude, radius=radius)
        app.logger.info("%s Successfully fetched profiles within radius /fetchprofileswithinradius" % (userId))
        return jsonify(profilesArray)
    except Exception as e:
        app.logger.exception(
            "%s Failed to get profiles within given radius locataion for user in /fetchprofileswithinradius" % (userId))
        app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /fetchprofileswithinradius')


# Invoked on Report Profile request from a user.
@app.route('/reportProfile', methods=['POST'])
@validateCookie
def report_profiles(decoded_claims=None):
    """
    Endpoint to store likes, superlikes, dislikes, liked_by, disliked_by, superliked_by for users
        Body of Request contains following payloads:
        - current user id
        - reported profile id
    """
    try:
        userId = decoded_claims['user_id']
        current_user_id = request.json['current_user_id']
        reported_profile_id = request.json['other_user_id']
        reason_given = request.json['reasonGiven']
        description_given = request.json['descriptionGiven']
        db.collection('ReportedProfile').document(reported_profile_id).collection(userId).document(
            "ReportingDetails").set({"reportedById": userId,
                                     "idBeingReported": reported_profile_id,
                                     "reasonGiven": reason_given,
                                     "descriptionGiven": description_given,
                                     "timestamp": time.time()
                                     })
        future = run_coroutine(unmatch_task_function(current_user_id, reported_profile_id))
        results = future.result()
        app.logger.info("%s Successfully reported profile /fetchprofileswithinradius" % (userId))
        return jsonify({'status': 200})
    except Exception as e:
        app.logger.exception("%s Failed to report profile on /reportProfile" % (userId))
        app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /reportProfile')


# Invoked on Unmatch request from a user.
@app.route('/unmatch', methods=['POST'])
@validateCookie
def unmatch(decoded_claims=None):
    """
    Endpoint to store likes, superlikes, dislikes, liked_by, disliked_by, superliked_by for users
        Body of Request contains following payloads:
        - current user id
        - reported profile id
    """
    try:
        start = time.time()
        userId = decoded_claims['user_id']
        current_user_id = request.json['current_user_id']
        other_user_id = request.json['other_user_id']
        future = run_coroutine(unmatch_task_function(current_user_id, other_user_id))
        results = future.result()
        app.logger.info(f"Successfully unmatched {other_user_id} from {current_user_id}'s matches.")
        app.logger.info(f"API Execution Time: {time.time() - start}")
        return jsonify({'status': 200})
    except Exception as e:
        app.logger.exception(f"Failed to unmatch {other_user_id} from {current_user_id}'s matches.")
        app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /unmatch')


if __name__ == '__main__':
    app.run(debug=True)
