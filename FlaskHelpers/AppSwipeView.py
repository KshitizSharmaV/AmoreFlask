import flask
from flask import Blueprint, current_app, jsonify, request
import traceback
from ProjectConf.AsyncioPlugin import run_coroutine
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.FirestoreConf import db
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers
from FlaskHelpers.FetchProfiles import get_profiles
from FlaskHelpers.FirestoreFunctions import swipe_tasks_future as store_like_dislike_task
import requests
import json
import logging

app_swipe_view_app = Blueprint('AppSwipeView', __name__)
logger = logging.getLogger()


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
        profiles_array = get_profiles(user_id=decoded_claims['user_id'], ids_already_in_deck=request.json["idsAlreadyInDeck"])
        logger.info("%s Successfully fetched profile /fetchprofiles" % (user_id))
        return jsonify(profiles_array)
    except Exception as e:
        logger.exception("%s Failed to fetch profile in /fetchprofiles " % (user_id))
        logger.exception(traceback.format_exc())
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
            "currentUserId":request.json['currentUserID'],
            "swipeInfo":request.json['swipeInfo'],
            "swipedUserId": request.json['swipedUserID']
        }
        response = requests.post(f"{cachingServerRoute}/storelikesdislikesGate",
                                data=json.dumps(requestData), 
                                headers=headers)
        logger.info(f"Successfully stored LikesDislikes:{request.json['currentUserID']}:{request.json['swipeInfo']}:{request.json['swipedUserID']}")
        return jsonify({'status': 200})
    except Exception as e:
        logger.exception(
            "%s Failed to get store likes, dislikes or supelikes in post request to in /storelikesdislikes" % (userId))
        logger.exception(traceback.format_exc())
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
        current_user_id = request.json['currentUserID']
        swipe_info = request.json['swipeInfo']
        swiped_user_id = request.json['swipedUserID']
        # db.collection('LikesDislikes').document(current_user_id).set({"wasUpdated":True}) - No Need of this statement
        db.collection('LikesDislikes').document(current_user_id).collection("Given").document(swiped_user_id).delete()
        db.collection('LikesDislikes').document(swiped_user_id).collection("Received").document(
            current_user_id).delete()
        logger.info(f" Successfully rewinded {swipe_info} by {userId}")
        return jsonify({'status': 200})
    except Exception as e:
        logger.exception(
            "%s Failed to get store likes, dislikes or supelikes in post request to in /storelikesdislikes" % (userId))
        logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /storelikesdislikes')
