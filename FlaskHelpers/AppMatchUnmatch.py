import flask
from flask import Blueprint, current_app, jsonify, request
import json
import logging
import time

import requests
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers
from ProjectConf.AuthenticationDecorators import validateCookie

app_match_unmatch = Blueprint('AppMatchUnmatch', __name__)

# Invoked on Unmatch request from a user.
@current_app.route('/unmatch', methods=['POST'])
@validateCookie
def unmatch(decoded_claims=None):
    """
    Endpoint to store likes, superlikes, dislikes, liked_by, disliked_by, superliked_by for users
        Body of Request contains following payloads:
        - current user id
        - reported profile id
    """
    try:
        userId = decoded_claims['user_id']
        other_user_id, current_user_id = request.json['other_user_id'], request.json['current_user_id']
        request_data = {
            'current_user_id': current_user_id,
            'other_user_id': other_user_id
        }
        response = requests.post(f"{cachingServerRoute}/unmatchgate",
                                 data=json.dumps(request_data),
                                 headers=headers)
        current_app.logger.info(f"Successfully unmatched {other_user_id} from {current_user_id}'s matches.")
        return jsonify({'status': 200})
    except Exception as e:
        current_app.logger.error("%s Failed to unmatch the profile" % (userId))
        current_app.logger.exception(e)
        return flask.abort(401, 'An error occured in API /unmatch')



@current_app.route('/loadmatchesunmatches',methods=['POST'])
@validateCookie
def store_match_unmatch_in_redis_gateway(decoded_claims=None):
    """
    Endpoint to store match unmatch data for user in the redis
        Body of Request contains following payloads:
        - current user id
        - fromCollection: Match or Unmatch
    """
    try:
        userId = decoded_claims['user_id']

        # Load the Unmatch profiles for the user
        # We don't need the unmatched profiles data but we want to save them in cache
        profiles_array = requests.post(f"{cachingServerRoute}/loadmatchesunmatchesgate",
                                 data=json.dumps({'userId': userId, 'fromCollection':'Unmatch'}),
                                 headers=headers)
        profiles_array = profiles_array.json()
        current_app.logger.info(f"Matchunmatch:{userId}:Unmatch successfully stored unmatch in redis {len(profiles_array)}")
        
        # Load the match profile for the user into cache & send back the profiles to user
        profiles_array = requests.post(f"{cachingServerRoute}/loadmatchesunmatchesgate",
                                 data=json.dumps({'userId': userId, 'fromCollection':'Match'}),
                                 headers=headers)
        profiles_array = profiles_array.json()
        current_app.logger.info(f"Matchunmatch:{userId}:Match successfully stored match in redis {len(profiles_array)}")

        return jsonify(profiles_array)
    except Exception as e:
        current_app.logger.error(f"{userId} Failed to store the match unmatch for ")
        current_app.logger.exception(e)
        return flask.abort(401, 'An error occured in API /loadmatchesunmatches')