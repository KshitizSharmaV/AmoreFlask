import flask
from flask import Blueprint, current_app,  Flask, jsonify, request
import traceback, time

from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.FirestoreConf import db
from Services.FetchProfiles import getProfiles

app_swipe_view_app = Blueprint('AppSwipeView', __name__)

# fetch_profiles is used to get profiles for cards in swipe view
@current_app.route('/fetchprofiles', methods=['POST'])
@validateCookie
def fetch_profiles(decoded_claims=None):
    """
    :accepts:
    - n =  no. of profiles
    - radius = radius of search
    - current location of user
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
        profilesArray = getProfiles(userId=decoded_claims['user_id'],
                                        idsAlreadyInDeck=request.json["idsAlreadyInDeck"])
        current_app.logger.info("%s Successfully fetched profile /fetchprofiles" %(userId))
        return jsonify(profilesArray)
    except Exception as e:
        current_app.logger.exception("%s Failed to fetch profile in /fetchprofiles " %(userId))
        current_app.logger.exception(traceback.format_exc())
    flask.abort(401, 'An error occured in /fetchprofiles')


# store_likes_dislikes_superlikes store likes, dislikes and superlikes in own user id and other profile being acted on
@current_app.route('/storelikesdislikes', methods=['POST'])
@validateCookie
def store_likes_dislikes_superlikes(decoded_claims=None):
    """
    Endpoint to store likes, superlikes, dislikes, liked_by, disliked_by, superliked_by for users
    """
    try:
        """
        Body of Request contains following payloads:
        - current user id
        - swipe info: Like, Dislike, Superlike
        - swiped profile id
        """
        userId = decoded_claims['user_id']
        current_user_id = request.json['currentUserID']
        swipe_info = request.json['swipeInfo']
        swiped_user_id = request.json['swipedUserID']
        db.collection('LikesDislikes').document(current_user_id).collection(swipe_info).document(swiped_user_id).set(
            {"id": swiped_user_id, "timestamp": time.time()})
        by_collection = "LikedBy" if swipe_info == "Likes" else "DislikedBy" if swipe_info == "Dislikes" else "SuperlikedBy"
        db.collection('LikesDislikes').document(swiped_user_id).collection(by_collection).document(current_user_id).set(
            {"id": current_user_id, "timestamp": time.time()})
        current_app.logger.info("%s %s %s"  %(userId,swipe_info,swiped_user_id))
        return jsonify({'status': 200})
    except Exception as e:
        current_app.logger.exception("%s Failed to get store likes, dislikes or supelikes in post request to in /storelikesdislikes"  %(userId)) 
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /storelikesdislikes')

# store_likes_dislikes_superlikes store likes, dislikes and superlikes in own user id and other profile being acted on
@current_app.route('/rewindswipesingle', methods=['POST'])
@validateCookie
def rewind_likes_dislikes_superlikes(decoded_claims=None):
    """
    Endpoint to rewind last swiped card, and modify appropriate firestore subcollections.
    """
    try:
        """
        Body of Request contains following payloads:
        - current user id
        - swipe info: Like, Dislike, Superlike
        - swiped profile id
        """
        userId = decoded_claims['user_id']
        current_user_id = request.json['currentUserID']
        swipe_info = request.json['swipeInfo']
        swiped_user_id = request.json['swipedUserID']
        db.collection('LikesDislikes').document(current_user_id).collection(swipe_info).document(swiped_user_id).delete()
        by_collection = "LikedBy" if swipe_info == "Likes" else "DislikedBy" if swipe_info == "Dislikes" else "SuperlikedBy"
        db.collection('LikesDislikes').document(swiped_user_id).collection(by_collection).document(current_user_id).delete()
        print("Successfully rewinded", current_user_id, swipe_info, swiped_user_id)
        current_app.logger.info(f" Successfully rewinded {swipe_info} by {userId}")
        return jsonify({'status': 200})
    except Exception as e:
        current_app.logger.exception("%s Failed to get store likes, dislikes or supelikes in post request to in /storelikesdislikes"  %(userId)) 
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /storelikesdislikes')