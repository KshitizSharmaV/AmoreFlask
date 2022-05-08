

import flask
from flask import Blueprint, current_app, jsonify, request
import json
import logging
import time
import geohash2

from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.FirestoreConf import db

app_geo_hash = Blueprint('appGeoHash', __name__)
logger = logging.getLogger()

@current_app.route('/getgeohash', methods=['POST'])
@validateCookie
def get_geohash_for_location(decoded_claims=None):
    """
    Endpoint to get Geohash for given latitude and longitude
    Body of Request contains following payloads:
    - latitude
    - longitude
    - precision
    While Updating the Filters and Location, get Geohash for the user location
    """
    try:
        userId = decoded_claims['user_id']
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        precision = int(request.json['precision'])
        geohash = geohash2.encode(latitude=latitude, longitude=longitude, precision=precision)
        logger.info("%s Successfully got geo hash for location /getgeohash" % (userId))
        return jsonify({'geohash': geohash})
    except Exception as e:
        logger.exception("%s Failed to get geo locataion for user in /getgeohash" % (userId))
        logger.exception(e)
    return flask.abort(401, 'An error occured in API /getgeohash')

