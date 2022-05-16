from flask import Flask
import flask
import logging.config
import os
from datetime import datetime

app = Flask(__name__)

with app.app_context():
    from FlaskHelpers.AppAuthentication import auth_app
    from FlaskHelpers.AppGeohash import app_geo_hash
    from FlaskHelpers.AppReportProfile import app_report_profile
    from FlaskHelpers.AppSuperLikesDislikes import app_super_likes_dislikes
    from FlaskHelpers.AppSwipeView import app_swipe_view_app
    from FlaskHelpers.AppUnswipe import app_unswipe


LOGGING_CONFIG = { 
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': { 
        'default': { 
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': { 
        '': {  # root logger
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
        'my.packg': { 
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
        '__main__': {  # if __name__ == '__main__'
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
    } 
}

logging.config.dictConfig(LOGGING_CONFIG)


app.logger.info('Config')

import json
@app.route("/test", methods=["Get"])
def test():
    try:
        app.logger.info("Test Called")
        return json.dumps({"status":True})
    except Exception as e:
        app.logger.exception("Failed to get test started")
        app.logger.exception(e)
    return flask.abort(401, 'An error occured in API /getgeohash')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
    app.logger.info("Starting Amore Flask")
