from flask import Flask, g
import time
import flask
import requests
import logging.config
from ProjectConf.ReadFlaskYaml import *
import os
from datetime import datetime
# Imports the Cloud Logging client library
import google.cloud.logging
from ProjectConf.FirestoreConf import cred

app = Flask(__name__)

with app.app_context():
    from FlaskHelpers.AppAuthentication import auth_app
    from FlaskHelpers.AppGeohash import app_geo_hash
    from FlaskHelpers.AppReportProfile import app_report_profile
    from FlaskHelpers.AppSuperLikesDislikes import app_super_likes_dislikes
    from FlaskHelpers.AppSwipeView import app_swipe_view_app
    from FlaskHelpers.AppMessage import app_message
    from FlaskHelpers.AppMatchUnmatch import app_match_unmatch
    from FlaskHelpers.AppProfiles import app_profile

@app.before_first_request
def setup_logging():
    if not app.debug:
        # Instantiates a client
        client = google.cloud.logging.Client(credentials=cred.get_credential())

        # Retrieves a Cloud Logging handler based on the environment
        # you're running in and integrates the handler with the
        # Python logging module. By default this captures all logs
        # at INFO level and higher
        client.setup_logging()
        # In production mode, add log handler to sys.stderr.
        # app.logger.setLevel(logging.INFO)
        # app.logger.addHandler(logging.StreamHandler(sys.stdout))

@app.before_request
def before_request():
    g.start = time.time()

@app.after_request
def after_request(response):
    diff = time.time() - g.start
    app.logger.debug(f"Total server side exec time: {diff}")
    return response

import json
@app.route("/test", methods=["Get"])
def test():
    try:
        app.logger.info("Test Called")
        response = requests.get(f"{cachingServerRoute}/test",headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return json.dumps({"status": False})
    except Exception as e:
        app.logger.exception("Failed to get test started")
        app.logger.exception(e)
    return flask.abort(401, 'An error occured in API /getgeohash')

if __name__ == '__main__':
    # app.run(host="0.0.0.0", debug=True)
    app.run(host="127.0.0.1", port=5040, debug=True)
    app.logger.info("Starting Amore Flask")
