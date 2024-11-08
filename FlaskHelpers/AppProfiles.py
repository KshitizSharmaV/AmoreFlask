import flask
from flask import Blueprint, current_app, jsonify, request
import json
import logging
import time
import requests

from ProjectConf.AsyncioPlugin import run_coroutine
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers


app_profile = Blueprint('AppProfiles', __name__)
logger = logging.getLogger()


# Invoked on Report Profile request from a user.
@current_app.route('/storeProfileInBackend', methods=['POST'])
@validateCookie
def post_profile_to_backend(decoded_claims=None):
    """
    Endpoint to store likes, superlikes, dislikes, liked_by, disliked_by, superliked_by for users
        Body of Request contains following payloads:
        - current user id
        - reported profile id
    """
    try:
        userId = decoded_claims['user_id']
        current_app.logger.info(userId)
        requestData = {
            "profile": request.json['profile']
        }
        response = requests.post(f"{cachingServerRoute}/storeProfileInBackendGate",
                                 data=json.dumps(requestData),
                                 headers=headers)
        current_app.logger.info(f"{userId}: Sent successfully from /storeProfileInBackend")
        response = jsonify({'message':"Success"})
        response.status_code = 200
        return response
    except Exception as e:
        current_app.logger.error(f"{userId}: Unable to to caching service for storage /storeProfileInBackend")
        current_app.logger.exception(e)
        response = jsonify({'message': 'An error occured in API /storeProfileInBackend'})
        response.status_code = 400
        return response
        
# Function expects a complete profile of the
@current_app.route('/fetchGeoRecommendations', methods=['POST'])
@validateCookie
def fetch_recommendation_for_user(decoded_claims=None):
    try:
        current_app.logger.info(f"/fetchGeoRecommendations API TRIGGERED.")
        userId = decoded_claims['user_id']
        current_app.logger.info(userId)
        requestData = {
            "userId": userId,
            "profilesAlreadyInDeck": request.json['profilesAlreadyInDeck'],
            "filterData": request.json['filterData']
        }
        response = requests.post(f"{cachingServerRoute}/fetchGeoRecommendationsGate",
                                 data=json.dumps(requestData),
                                 headers=headers)
        if response.status_code == 200:
            response = response.json()
            for profile in response:
                if profile.get('location') and profile.get('location').get('latitude') and profile.get('location').get('longitude'):
                    if type(profile['location']['latitude']) != float or type(profile['location']['longitude']) != float:
                        profile['location']['latitude'] = float(profile['location']['latitude'])
                        profile['location']['longitude'] = float(profile['location']['longitude'])
            current_app.logger.info(f"{userId}: Successfully fetched recommendations for user")
            # current_app.logger.info(f"{response}")
            # response = jsonify({'message':"Success"})
            # response.status_code = 200
            return jsonify(response)
        else:
            current_app.logger.error(f"{userId}: Unable to to fetch recommendations for user")    
    except Exception as e:
        current_app.logger.error(f"{userId}: Unable to to fetch recommendations for user")
        current_app.logger.exception(e)
        response = jsonify({'message': 'An error occured'})
        response.status_code = 400
        return response
