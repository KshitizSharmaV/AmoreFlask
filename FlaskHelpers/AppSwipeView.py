import flask
from flask import Blueprint, current_app, jsonify, request
import traceback
from ProjectConf.AsyncioPlugin import run_coroutine
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers
from FlaskHelpers.FetchProfiles import get_profiles
import requests
import json
import logging

app_swipe_view_app = Blueprint('AppSwipeView', __name__)
logger = logging.getLogger()

"""
All APIs ported to Amore Caching Server
"""


# fetch_profiles is used to get profiles for cards in swipe view
@current_app.route('/fetchprofiles', methods=['POST'])
@validateCookie
def fetch_profiles(decoded_claims=None):
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
    try:
        user_id = decoded_claims['user_id']
        profiles_array = get_profiles(user_id=user_id, ids_already_in_deck=request.json["idsAlreadyInDeck"])
        current_app.logger.info("%s Successfully fetched profile /fetchprofiles" % (user_id))
        return jsonify(profiles_array)
    except Exception as e:
        current_app.logger.exception("%s Failed to fetch profile in /fetchprofiles " % (user_id))
        current_app.logger.exception(traceback.format_exc())
    flask.abort(401, 'An error occured in /fetchprofiles')


# store_likes_dislikes_superlikes store likes, dislikes and superlikes in own user id and other profile being acted on
@current_app.route('/storelikesdislikes', methods=['POST'])
@validateCookie
def store_likes_dislikes_superlikes(decoded_claims=None):
    """
    Endpoint to store likes, superlikes, dislikes, liked_by, disliked_by, superliked_by for users
    """
    try:
        """
        Body of Request contains following payloads:
        - current user id
        - swipe info: Like, Dislike, Superlike
        - swiped profile id
        """
        userId = decoded_claims['user_id']
        requestData = {
            "currentUserId": request.json['currentUserID'],
            "swipeInfo": request.json['swipeInfo'],
            "swipedUserId": request.json['swipedUserID']
        }
        response = requests.post(f"{cachingServerRoute}/storelikesdislikesGate",
                                 data=json.dumps(requestData),
                                 headers=headers)
        current_app.logger.info(
            f"Successfully stored LikesDislikes:{request.json['currentUserID']}:{request.json['swipeInfo']}:{request.json['swipedUserID']}")
        return jsonify({'status': 200})
    except Exception as e:
        current_app.logger.exception(
            "%s Failed to get store likes, dislikes or supelikes in post request to in /storelikesdislikes" % (userId))
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /storelikesdislikes')


# store_likes_dislikes_superlikes store likes, dislikes and superlikes in own user id and other profile being acted on
@current_app.route('/rewindswipesingle', methods=['POST'])
@validateCookie
def rewind_likes_dislikes_superlikes(decoded_claims=None):
    """
    Endpoint to rewind last swiped card, and modify appropriate firestore subcollections.
    """
    try:
        """
        Body of Request contains following payloads:
        - current user id
        - swipe info: Like, Dislike, Superlike
        - swiped profile id
        """
        userId = decoded_claims['user_id']
        request_data = {
            'currentUserID': request.json['currentUserID'],
            'swipeInfo': request.json['swipeInfo'],
            'swipedUserID': request.json['swipedUserID']
        }
        response = requests.post(f"{cachingServerRoute}/rewindsingleswipegate",
                                 data=json.dumps(request_data),
                                 headers=headers)
        current_app.logger.info(f" Successfully rewinded {request.json['swipeInfo']} by {userId}")
        return jsonify({'status': 200})
    except Exception as e:
        current_app.logger.exception(
            "%s Failed to rewind" % (userId))
        current_app.logger.exception(traceback.format_exc())
        return flask.abort(401, 'An error occured in API /rewind')
