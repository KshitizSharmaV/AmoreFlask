import flask
from flask import Blueprint, current_app, jsonify, request
import json
import logging
import time

from ProjectConf.AsyncioPlugin import run_coroutine
from ProjectConf.AuthenticationDecorators import validateCookie
from FlaskHelpers.UnmatchHelper.UnmatchHelper import unmatch_task_function


app_get = Blueprint('appUnswipe', __name__)
logger = logging.getLogger()

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
        start = time.time()
        userId = decoded_claims['user_id']
        current_user_id = request.json['current_user_id']
        other_user_id = request.json['other_user_id']
        future = run_coroutine(unmatch_task_function(current_user_id, other_user_id))
        results = future.result()
        logger.info(f"Successfully unmatched {other_user_id} from {current_user_id}'s matches.")
        logger.info(f"API Execution Time: {time.time() - start}")
        return jsonify({'status': 200})
    except Exception as e:
        logger.error("%s Failed to unmatch the profile" % (userId))
        logger.exception(e)
    return flask.abort(401, 'An error occured in API /unmatch')
