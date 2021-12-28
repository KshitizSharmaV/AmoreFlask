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
        