import flask
from flask import Flask, jsonify, request
import traceback
import time
import logging.config
import os
from datetime import datetime

app = Flask(__name__)
from ProjectConf.FirestoreConf import db
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.AsyncioPlugin import run_coroutine

with app.app_context():
    from FlaskHelpers.AppAuthentication import auth_app
    from FlaskHelpers.AppSuperLikesDislikes import app_super_likes_dislikes
    from FlaskHelpers.AppSwipeView import app_swipe_view_app

# # Log Settings
LOG_FILENAME = datetime.now().strftime("%H_%M_%d_%m_%Y")+".log"
if not os.path.exists('Logs/AppLogs/'):
    os.makedirs('Logs/AppLogs/')
log_level = "DEBUG"

class LoggerConfig:
    dictConfig = {
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] {%(pathname)s:%(funcName)s:%(lineno)d} %(levelname)s - %(message)s',
        }},
        'handlers': {'default': {
                    'level': 'DEBUG',
                    'formatter': 'default',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': f'Logs/AppLogs/{LOG_FILENAME}',
                    'maxBytes': 5000000,
                    'backupCount': 10
                }},
        'root': {
            'level': log_level,
            'handlers': ['default']
        },
    }

logging.config.dictConfig(LoggerConfig.dictConfig)
logger = logging.getLogger()

import json
app.route("/test", method=["Get"])
def test():
    return json.dumps({"status":True})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
    logger.info("Starting Caching Service")
