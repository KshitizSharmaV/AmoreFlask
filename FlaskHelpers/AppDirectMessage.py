import flask
from flask import Blueprint, current_app, jsonify, request
import json
import logging
import time
import requests

from ProjectConf.AsyncioPlugin import run_coroutine
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers


app_direct_message = Blueprint('appDirectMessage', __name__)
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
        