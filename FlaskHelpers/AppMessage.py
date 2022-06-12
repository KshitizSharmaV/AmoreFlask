import flask
from flask import Blueprint, current_app, jsonify, request
import json
import logging
import time
import requests

from ProjectConf.AsyncioPlugin import run_coroutine
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers


app_message = Blueprint('appMessage', __name__)
logger = logging.getLogger()


# Invoked on Report Profile request from a user.
@current_app.route('/matchondirectmessage', methods=['POST'])
@validateCookie
def match_profiles_on_direct_message(decoded_claims=None):
    """
    Endpoint to match two profiles when the receiver of Direct Message approves DM request.
        Body of Request contains following payloads:
        - current user id
        - other user id
    """
    try:
        userId = decoded_claims['user_id']
        requestData = {
            "currentUserId": request.get_json().get('currentUserId'),
            "otherUserId": request.get_json().get('otherUserId')
        }
        response = requests.post(f"{cachingServerRoute}/matchondirectmessageGate",
                                 data=json.dumps(requestData),
                                 headers=headers)
        if response.status_code == 200:
            current_app.logger.info(f"/matchondirectmessageGate: Successfully matched {requestData['currentUserId']} and {requestData['otherUserId']}")
        else:
            current_app.logger.info(f"/matchondirectmessageGate: Failed to match {requestData['currentUserId']} and {requestData['otherUserId']}")
        response = jsonify({'message':"Success"})
        response.status_code = 200
        return response
    except Exception as e:
        current_app.logger.error(f"/matchondirectmessageGate: Failed to match {requestData['currentUserId']} and {requestData['otherUserId']}")
        current_app.logger.exception(e)
        response = jsonify({'message': 'An error occured in API /storeProfileInBackend'})
        response.status_code = 400
        return response
        

@current_app.route('/loadallchatprofiles',methods=['POST', 'GET'])
@validateCookie
def fetch_all_chat_profiles(decoded_claims=None):
    """
    Endpoint to fetch all chat profiles data and store them in Redis if not present
    Uses /getprofilesbyids endpoint on Caching Service
        Body of Request contains following payloads:
        - allChatUserIds: list
    """
    try:
        userId = decoded_claims['user_id']
        request_body = {
            "profileIdList": request.get_json().get('allChatUserIds')
        }
        profiles_array = requests.get(f"{cachingServerRoute}/getprofilesbyids",
                                            data=json.dumps(request_body),
                                            headers=headers)
        profiles_array = profiles_array.json()
        current_app.logger.info(f"Chat Profiles:{userId}:Chat Profiles successfully fetched from and stored in redis {len(profiles_array)}")
        return jsonify(profiles_array)
    except Exception as e:
        current_app.logger.error(f"{userId} Failed to fetch all chat profiles ")
        current_app.logger.exception(e)
        return flask.abort(401, 'An error occured in API /loadallchatprofiles')