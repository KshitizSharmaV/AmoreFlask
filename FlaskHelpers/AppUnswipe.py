import flask
from flask import Blueprint, current_app, jsonify, request
import json
import logging
import time

import requests
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers
from ProjectConf.AuthenticationDecorators import validateCookie

app_unswipe = Blueprint('AppUnswipe', __name__)
logger = logging.getLogger()

"""
All APIs ported to Amore Caching Server
"""


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
        logger.info("Entering Unmatch API")
        start = time.time()
        userId = decoded_claims['user_id']
        other_user_id, current_user_id = request.json['other_user_id'], request.json['current_user_id']
        request_data = {
            'current_user_id': current_user_id,
            'other_user_id': other_user_id
        }
        response = requests.post(f"{cachingServerRoute}/unmatchgate",
                                 data=json.dumps(request_data),
                                 headers=headers)
        logger.info(f"Successfully unmatched {other_user_id} from {current_user_id}'s matches.")
        logger.info(f"API Execution Time: {time.time() - start}")
        return jsonify({'status': 200})
    except Exception as e:
        logger.error("%s Failed to unmatch the profile" % (userId))
        logger.exception(e)
        return flask.abort(401, 'An error occured in API /unmatch')
