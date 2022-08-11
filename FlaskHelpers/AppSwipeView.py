import flask
from flask import Blueprint, current_app, jsonify, request
import traceback
from ProjectConf.AsyncioPlugin import run_coroutine
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers
import requests
import json
import logging

app_swipe_view_app = Blueprint('AppSwipeView', __name__)

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
            'currentUserID': request.get_json().get('currentUserID')
        }
        rewinded_user_info = requests.post(f"{cachingServerRoute}/rewindsingleswipegate",
                                 data=json.dumps(request_data),
                                 headers=headers)
        current_app.logger.info(f" Successfully rewinded last swipe by {request_data['currentUserID']}")
        return jsonify(rewinded_user_info.json())
    except Exception as e:
        current_app.logger.exception(
            "%s Failed to rewind" % (userId))
        current_app.logger.exception(traceback.format_exc())
        return flask.abort(401, 'An error occured in API /rewind')
