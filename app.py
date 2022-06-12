from flask import Flask
import flask
import requests
import logging.config
from ProjectConf.ReadFlaskYaml import *
import os
from datetime import datetime

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
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


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
