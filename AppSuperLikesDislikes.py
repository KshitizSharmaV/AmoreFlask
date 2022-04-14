import flask
from flask import Blueprint, current_app, Flask, jsonify, request
import traceback, time
import asyncio
from ProjectConf import loop
from ProjectConf.AuthenticationDecorators import validateCookie
from ProjectConf.FirestoreConf import db, async_db
from Services.FetchProfiles import getProfiles, getProfilesForListOfIds, likesGiven, superLikesGiven, dislikesGiven, \
    likesReceived, dislikesLikesReceived, superLikesReceived, elitePicks

app_super_likes_dislikes = Blueprint('AppSuperLikesDislikes', __name__)
paramsReceivedFuncMapping = {"likesGiven": likesGiven,
                             "superLikesGiven": superLikesGiven,
                             "dislikesGiven": dislikesGiven,
                             "likesReceived": likesReceived,
                             "dislikesLikesReceived": dislikesLikesReceived,
                             "superLikesReceived": superLikesReceived,
                             "elitePicks": elitePicks}


# Common route to be called from Elite, Likes Given and Likes Received Views
@current_app.route('/commonfetchprofiles', methods=['POST', 'GET'])
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
        current_app.logger.info("%s fetched profiles from %s: %s" % (userId, fromCollection, str(len(profilesArray))))
        return jsonify(profilesArray)
    except Exception as e:
        current_app.logger.exception(
            "%s failed to fetch profiles in /commonfetchprofiles from %s" % (userId, fromCollection))
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, '%s failed to fetch profiles in /commonfetchprofiles from %s' % (userId, fromCollection))


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
        loop.run_until_complete(
            like_dislike_superlike_task(current_user_id=current_user_id, swiped_user_id=swiped_user_id,
                                        swipe_info=swipe_info))
        # db.collection('LikesDislikes').document(current_user_id).set({"wasUpdated":True})
        # db.collection('LikesDislikes').document(current_user_id).collection("Given").document(swiped_user_id).set({"swipe":swipe_info,"timestamp": time.time(),'matchVerified':False})
        # db.collection('LikesDislikes').document(swiped_user_id).collection("Received").document(current_user_id).set({"swipe":swipe_info,"timestamp": time.time()})
        current_app.logger.info(f" Successfullu upgraded from like to superlike {swipe_info} by {userId}")
        return jsonify({'status': 200})
    except Exception as e:
        current_app.logger.exception(
            "%s Failed to get store likes, dislikes or supelikes in post request to in /storelikesdislikes" % (userId))
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /storelikesdislikes')


async def like_dislike_superlike_task(current_user_id, swiped_user_id, swipe_info):
    task1 = asyncio.create_task(was_updated_task(current_user_id, swiped_user_id, swipe_info))
    task2 = asyncio.create_task(given_swipe_task(current_user_id, swiped_user_id, swipe_info))
    task3 = asyncio.create_task(received_swipe_task(current_user_id, swiped_user_id, swipe_info))
    return asyncio.gather(*[task1, task2, task3])


async def was_updated_task(current_user_id, swiped_user_id, swipe_info):
    await async_db.collection('LikesDislikes').document(current_user_id).set({"wasUpdated": True})


async def given_swipe_task(current_user_id, swiped_user_id, swipe_info):
    await async_db.collection('LikesDislikes').document(current_user_id).collection("Given").document(
        swiped_user_id).set(
        {"swipe": swipe_info, "timestamp": time.time(), 'matchVerified': False})


async def received_swipe_task(current_user_id, swiped_user_id, swipe_info):
    await async_db.collection('LikesDislikes').document(swiped_user_id).collection("Received").document(
        current_user_id).set(
        {"swipe": swipe_info, "timestamp": time.time()})
