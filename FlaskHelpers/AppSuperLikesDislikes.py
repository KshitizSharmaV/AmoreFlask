import asyncio
import flask
import requests
import json
from flask import Blueprint, current_app, jsonify, request
import traceback
import logging
from ProjectConf import loop
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.AsyncioPlugin import *
from FlaskHelpers.ExtSuperLikesDislikes import likes_given, super_likes_given, dislikes_given, likes_received, dislikes_received, super_likes_received, elite_picks
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers

app_super_likes_dislikes = Blueprint('AppSuperLikesDislikes', __name__)
paramsReceivedFuncMapping = {"likesGiven": likes_given,
                             "superLikesGiven": super_likes_given,
                             "dislikesGiven": dislikes_given,
                             "likesReceived": likes_received,
                             "dislikesLikesReceived": dislikes_received,
                             "superLikesReceived": super_likes_received,
                             "elitePicks": elite_picks}

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
        noOfLastRecords = request.get_json().get('noOfLastRecords')
        profiles_array = paramsReceivedFuncMapping[from_collection](userId=user_id, noOfLastRecords=noOfLastRecords)
        for profile in profiles_array:
            if not profile.get('location') and profile.get('location').get('latitude') and profile.get('location').get('latitude'):
                continue
            if type(profile['location']['latitude']) != float or type(profile['location']['longitude']) != float:
                profile['location']['latitude'] = float(profile['location']['latitude'])
                profile['location']['longitude'] = float(profile['location']['longitude'])
        current_app.logger.info("%s fetched profiles from %s: %s" % (user_id, from_collection, str(len(profiles_array))))
        return jsonify(profiles_array)
    except Exception as e:
        current_app.logger.exception(
            "%s failed to fetch profiles in /commonfetchprofiles from %s" % (user_id, from_collection))
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, '%s failed to fetch profiles in /commonfetchprofiles from %s' % (user_id, from_collection))


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
            "swipedUserId": request.json['swipedUserID'],
            "upgradeLikeToSuperlike": True
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
