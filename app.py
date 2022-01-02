import flask
from flask import Flask, jsonify, request
import traceback
import time
import geohash2
import logging
from time import strftime

app = Flask(__name__)

from ProjectConf.FirestoreConf import db
from ProjectConf.AuthenticationDecorators import auth_decorators_app, validateCookie
with app.app_context():
    from AppAuthentication import auth_app
    from AppSuperLikesDislikes import app_super_likes_dislikes
    from AppSwipeView import app_swipe_view_app
from Services.FetchProfiles import get_profiles_within_radius,getProfiles

logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app.logger.setLevel(logging.INFO)

@app.route('/getgeohash', methods=['POST'])
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
        app.logger.info("%s Successfully got geo hash for location /getgeohash"  %(userId))
        return jsonify({'geohash': geohash})
    except Exception as e:
        app.logger.exception("%s Failed to get geo locataion for user in /getgeohash"  %(userId))
        app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /getgeohash')


# fetch_profiles within given radius for cards in swipe view
@app.route('/fetchprofileswithinradius', methods=['POST'])
@validateCookie
def fetch_profiles_within_given_radius(decoded_claims=None):
    """
    :accepts:
    - n =  no. of profiles
    - radius = radius of search
    - Current location of user -- Latitude, Longitude
    - id token
    :process:
    - verify id token
    - get all users uid (Will be refined for querying within a particular radius)
    - filter and sort based on Recommendation Engine
    - eliminate user uids present in current user's Likes and Dislikes
    - pick n top uids from rest of the uids
    :return:
    - array of n uids
    """
    try:
        userId = decoded_claims['user_id']
        idsAlreadyInDeck = request.json["idsAlreadyInDeck"]
        latitude = request.json['latitude']
        longitude = request.json['longitude']
        radius = int(request.json['radius'])
        profilesArray = get_profiles_within_radius(userId=userId, idsAlreadyInDeck=idsAlreadyInDeck, latitude=latitude, longitude=longitude, radius=radius)
        app.logger.info("%s Successfully fetched profiles within radius /fetchprofileswithinradius"  %(userId))
        return jsonify(profilesArray)
    except Exception as e:
        app.logger.exception("%s Failed to get profiles within given radius locataion for user in /fetchprofileswithinradius" %(userId))
        app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /fetchprofileswithinradius')



# every time a user swipes the application calls this api to store data in collection
@app.route('/reportProfile', methods=['POST']) 
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
        reported_profile_id = request.json['swipedProfileID']
        reason_given = request.json['reasonGiven']
        description_given = request.json['descriptionGiven']
        db.collection('ReportedProfile').document(reported_profile_id).collection(userId).document("ReportingDetails").set({"reportedById": userId, 
                                                                        "idBeingReported":reported_profile_id,
                                                                        "reasonGiven":reason_given,
                                                                        "descriptionGiven":description_given,
                                                                        "timestamp": time.time()
                                                                    })
        app.logger.info("%s Successfully reported profile /fetchprofileswithinradius"  %(userId))
        return jsonify({'status': 200})
    except Exception as e:
        app.logger.exception("%s Failed to report profile on /reportProfile" %(userId))
        app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /reportProfile')    


if __name__ == '__main__':
    app.run(debug=True)
