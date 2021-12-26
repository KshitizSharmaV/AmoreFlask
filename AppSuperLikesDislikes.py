import flask
from flask import Blueprint, current_app,  Flask, jsonify, request
import traceback, time

from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.FirestoreConf import db
from Services.FetchProfiles import getProfiles
from Services.FetchProfiles import superLikedProfilesByUser, getProfilesForListOfIds

app_super_likes_dislikes = Blueprint('AppSuperLikesDislikes', __name__)

# fetch_likes_given is used to get profiles which are super liked by the user
@current_app.route('/fetchlikesgiven', methods=['POST'])
@validateCookie
def fetch_likes_given(decoded_claims=None):
    """
    :accepts:
    just the reponse cookie and we decode the user id then get profiles superliked by the user
    """
    try:
        userId = decoded_claims['user_id']
        superLikedIdsList = superLikedProfilesByUser(userId=decoded_claims['user_id'])
        profilesArray = getProfilesForListOfIds(listofIds=superLikedIdsList)
        current_app.logger.info("%s Successfully fetches likes given /fetchlikesgiven"  %(userId))
        return jsonify(profilesArray)
    except Exception as e:
        current_app.logger.exception("%s Failed to get fetch likes given in /fetchlikesgiven"  %(userId))
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /fetchlikesgiven')