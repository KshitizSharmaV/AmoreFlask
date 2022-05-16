import asyncio
import flask
import requests
import json
from flask import Blueprint, current_app, jsonify, request
import traceback
import logging
from ProjectConf import loop
from ProjectConf.AuthenticationDecorators import validateCookie
from FlaskHelpers.FirestoreFunctions import swipe_tasks_future as like_dislike_superlike_task
from FlaskHelpers.FetchProfiles import get_profiles_for_list_of_ids, likes_given, super_likes_given, dislikes_given, \
    likes_received, dislikes_received, super_likes_received, elite_picks
from ProjectConf.AsyncioPlugin import *
from FlaskHelpers.FetchProfiles import get_profiles_within_radius
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers

app_super_likes_dislikes = Blueprint('AppSuperLikesDislikes', __name__)
paramsReceivedFuncMapping = {"likesGiven": likes_given,
                             "superLikesGiven": super_likes_given,
                             "dislikesGiven": dislikes_given,
                             "likesReceived": likes_received,
                             "dislikesLikesReceived": dislikes_received,
                             "superLikesReceived": super_likes_received,
                             "elitePicks": elite_picks}
logger = logging.getLogger()

"""
APIs yet to be ported to Amore Caching Server
"""


# Common route to be called from Elite, Likes Given and Likes Received Views
@current_app.route('/commonfetchprofiles', methods=['POST', 'GET'])
@validateCookie
def fetch_profile_common_route(decoded_claims=None):
    """
    :accepts: client cookie
    the kind of data that needs to be fetched
    """
    user_id = ""
    from_collection = ""
    try:
        user_id = decoded_claims['user_id']
        from_collection = request.json['fromCollection']
        ids_list = paramsReceivedFuncMapping[from_collection](userId=user_id)
        future = run_coroutine(get_profiles_for_list_of_ids(list_of_ids=ids_list))
        profiles_array = future.result()
        current_app.logger.info(
            "%s fetched profiles from %s: %s" % (user_id, from_collection, str(len(profiles_array))))
        return jsonify(profiles_array)
    except Exception as e:
        current_app.logger.exception(
            "%s failed to fetch profiles in /commonfetchprofiles from %s" % (user_id, from_collection))
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, '%s failed to fetch profiles in /commonfetchprofiles from %s' % (user_id, from_collection))


# fetch_profiles within given radius for cards in swipe view
@current_app.route('/fetchprofileswithinradius', methods=['POST'])
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
        current_app.logger.info("%s Successfully fetched profiles within radius /fetchprofileswithinradius" % (userId))
        return jsonify(profilesArray)
    except Exception as e:
        current_app.logger.exception(
            "%s Failed to get profiles within given radius locataion for user in /fetchprofileswithinradius" % (userId))
        current_app.logger.exception(e)
    return flask.abort(401, 'An error occured in API /fetchprofileswithinradius')


"""
APIs Ported to Amore Caching Server
"""


# store_likes_dislikes_superlikes store likes, dislikes and superlikes in own user id and other profile being acted on
@current_app.route('/upgradeliketosuperlike', methods=['POST'])
@validateCookie
def upgrade_like_to_superlike(decoded_claims=None):
    """
    Endpoint to Upgrade Like to Superlike in the likes given page, and modify appropriate firestore subcollections.
    """
    try:
        """
        Body of Request contains following payloads:
        - current user id
        - swipe info: Like, Dislike, Superlike
        - swiped profile id

        -- Delete entry from Likes, LikedBy
        -- Make entry in Superlikes, SuperlikedBy
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
        current_app.logger.exception(e)
    return flask.abort(401, 'An error occured in API /storelikesdislikes')
