

import flask
from flask import Blueprint, current_app, jsonify, request
import json
import logging
import time


from ProjectConf.AsyncioPlugin import run_coroutine
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.FirestoreConf import db
from FlaskHelpers.UnmatchHelper.UnmatchHelper import unmatch_task_function

app_get = Blueprint('appReportProfile', __name__)
logger = logging.getLogger()


# Invoked on Report Profile request from a user.
@current_app.route('/reportProfile', methods=['POST'])
@validateCookie
def report_profiles(decoded_claims=None):
    """
    Endpoint to store likes, superlikes, dislikes, liked_by, disliked_by, superliked_by for users
        Body of Request contains following payloads:
        - current user id
        - reported profile id
    """
    try:
        userId = decoded_claims['user_id']
        current_user_id = request.json['current_user_id']
        reported_profile_id = request.json['other_user_id']
        reason_given = request.json['reasonGiven']
        description_given = request.json['descriptionGiven']
        db.collection('ReportedProfile').document(reported_profile_id).collection(userId).document(
            "ReportingDetails").set({"reportedById": userId,
                                     "idBeingReported": reported_profile_id,
                                     "reasonGiven": reason_given,
                                     "descriptionGiven": description_given,
                                     "timestamp": time.time()
                                     })
        future = run_coroutine(unmatch_task_function(current_user_id, reported_profile_id))
        results = future.result()
        logger.info("%s Successfully reported profile /reportProfile" % (userId))
        return jsonify({'status': 200})
    except Exception as e:
        logger.error("%s Failed to report profile on /reportProfile" % (userId))
        logger.exception(e)
    return flask.abort(401, 'An error occured in API /reportProfile')
