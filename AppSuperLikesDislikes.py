import flask
from flask import Blueprint, current_app,  Flask, jsonify, request
import traceback, time

from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.FirestoreConf import db
from Services.FetchProfiles import getProfiles, getProfilesForListOfIds, likesGiven, superLikesGiven, dislikesGiven, likesReceived, dislikesLikesReceived, superLikesReceived, elitePicks

app_super_likes_dislikes = Blueprint('AppSuperLikesDislikes', __name__)
paramsReceivedFuncMapping = {"likesGiven" : likesGiven,
           "superLikesGiven":superLikesGiven,
           "dislikesGiven":dislikesGiven,
           "likesReceived":likesReceived,
           "dislikesLikesReceived":dislikesLikesReceived,
           "superLikesReceived":superLikesReceived,
           "elitePicks":elitePicks}

# Common route to be called from Elite, Likes Given and Likes Received Views
@current_app.route('/commonfetchprofiles', methods=['POST','GET'])
@validateCookie
def fetchProfileCommonRoute(decoded_claims=None):
    """
    :accepts: client cookie
    the kind of data that needs to be fetched
    """
    try:
        userId = decoded_claims['user_id']
        fromCollection = request.json['fromCollection']
        idsList = paramsReceivedFuncMapping[fromCollection](userId=userId)
        profilesArray = getProfilesForListOfIds(listofIds=idsList)
        current_app.logger.info("%s fetched profiles from %s: %s"  %(userId,fromCollection,str(len(profilesArray))))
        return jsonify(profilesArray)
    except Exception as e:
        current_app.logger.exception("%s failed to fetch profiles in /commonfetchprofiles from %s"  %(userId,fromCollection))
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, '%s failed to fetch profiles in /commonfetchprofiles from %s' %(userId,fromCollection))
        
# store_likes_dislikes_superlikes store likes, dislikes and superlikes in own user id and other profile being acted on
@current_app.route('/upgradeliketosuperlike', methods=['POST'])
@validateCookie
def upgrade_like_to_superlike(decoded_claims=None):
    """
    Endpoint to Upgrade Like to Superlike in the likes given page, and modify appropriate firestore subcollections.
    """
    try:
        """
        Body of Request contains following payloads:
        - current user id
        - swipe info: Like, Dislike, Superlike
        - swiped profile id

        -- Delete entry from Likes, LikedBy
        -- Make entry in Superlikes, SuperlikedBy
        """
        userId = decoded_claims['user_id']
        current_user_id = request.json['currentUserID']
        swipe_info = request.json['swipeInfo']
        swiped_user_id = request.json['swipedUserID']

        db.collection('LikesDislikes').document(current_user_id).collection('Likes').document(swiped_user_id).delete()
        db.collection('LikesDislikes').document(current_user_id).collection(swipe_info).document(swiped_user_id).set(
            {"id": swiped_user_id, "timestamp": time.time()})
        by_collection = "LikedBy" if swipe_info == "Likes" else "DislikedBy" if swipe_info == "Dislikes" else "SuperlikedBy"
        db.collection('LikesDislikes').document(swiped_user_id).collection('LikedBy').document(current_user_id).delete()
        db.collection('LikesDislikes').document(swiped_user_id).collection(by_collection).document(current_user_id).set(
            {"id": current_user_id, "timestamp": time.time()})
        print("Successfully rewinded", current_user_id, swipe_info, swiped_user_id)
        current_app.logger.info(f" Successfully rewinded {swipe_info} by {userId}")
        return jsonify({'status': 200})
    except Exception as e:
        current_app.logger.exception("%s Failed to get store likes, dislikes or supelikes in post request to in /storelikesdislikes"  %(userId)) 
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /storelikesdislikes')