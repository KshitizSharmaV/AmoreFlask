import asyncio
import flask
from flask import Blueprint, current_app, jsonify, request
import traceback
from ProjectConf import loop
from ProjectConf.AuthenticationDecorators import validateCookie
from FlaskHelpers.FirestoreFunctions import swipe_tasks_future as like_dislike_superlike_task
from FlaskHelpers.FetchProfiles import get_profiles_for_list_of_ids, likes_given, super_likes_given, dislikes_given, \
    likes_received, dislikes_received, super_likes_received, elite_picks
from FlaskHelpers.AsyncioPlugin import *

app_super_likes_dislikes = Blueprint('AppSuperLikesDislikes', __name__)
paramsReceivedFuncMapping = {"likesGiven": likes_given,
                             "superLikesGiven": super_likes_given,
                             "dislikesGiven": dislikes_given,
                             "likesReceived": likes_received,
                             "dislikesLikesReceived": dislikes_received,
                             "superLikesReceived": super_likes_received,
                             "elitePicks": elite_picks}


# Common route to be called from Elite, Likes Given and Likes Received Views
@current_app.route('/commonfetchprofiles', methods=['POST', 'GET'])
@validateCookie
def fetch_profile_common_route(decoded_claims=None):
    """
    :accepts: client cookie
    the kind of data that needs to be fetched
    """
    user_id = ""
    from_collection = ""
    try:
        user_id = decoded_claims['user_id']
        from_collection = request.json['fromCollection']
        ids_list = paramsReceivedFuncMapping[from_collection](userId=user_id)
        future = run_coroutine(get_profiles_for_list_of_ids(list_of_ids=ids_list))
        profiles_array = future.result()
        current_app.logger.info(
            "%s fetched profiles from %s: %s" % (user_id, from_collection, str(len(profiles_array))))
        return jsonify(profiles_array)
    except Exception as e:
        current_app.logger.exception(
            "%s failed to fetch profiles in /commonfetchprofiles from %s" % (user_id, from_collection))
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, '%s failed to fetch profiles in /commonfetchprofiles from %s' % (user_id, from_collection))


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
        run_coroutine(like_dislike_superlike_task(current_user_id=current_user_id, swiped_user_id=swiped_user_id,
                                                  swipe_info=swipe_info))
        current_app.logger.info(f" Successfullu upgraded from like to superlike {swipe_info} by {userId}")
        return jsonify({'status': 200})
    except Exception as e:
        current_app.logger.exception(
            "%s Failed to get store likes, dislikes or supelikes in post request to in /storelikesdislikes" % (userId))
        current_app.logger.exception(traceback.format_exc())
    return flask.abort(401, 'An error occured in API /storelikesdislikes')
