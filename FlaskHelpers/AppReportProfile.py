import flask
from flask import Blueprint, current_app, jsonify, request
import json
import logging
import requests
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers

app_report_profile = Blueprint('appReportProfile', __name__)
logger = logging.getLogger()


# Invoked on Report Profile request from a user.
@current_app.route('/reportProfile', methods=['POST'])
@validateCookie
def report_profiles(decoded_claims=None):
    """
    Endpoint to Report a profile, either from Conversation View or Swipe View
        Body of Request contains following payloads:
        - Current User ID
        - Reported Profile ID
        - Reason for reporting
        - Description
    :return: Response contains success/failure status of reporting task.
    """
    try:
        userId = decoded_claims['user_id']
        request_data = {
            "current_user_id": request.get_json().get("current_user_id"), 
            "other_user_id": request.get_json().get("other_user_id"), 
            "reasonGiven": request.get_json().get("reasonGiven"), 
            "descriptionGiven": request.get_json().get("descriptionGiven")
        }
        response = requests.post(f"{cachingServerRoute}/reportprofilegate",
                                 data=json.dumps(request_data),
                                 headers=headers)
        response = response.json()
        current_app.logger.info("%s Successfully reported profile /reportProfile" % (userId))
        return jsonify(response)
    except Exception as e:
        current_app.logger.error("%s Failed to report profile on /reportProfile" % (userId))
        current_app.logger.exception(e)
    return flask.abort(401, 'An error occured in API /reportProfile')
