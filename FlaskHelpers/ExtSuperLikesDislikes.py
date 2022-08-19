import traceback
import asyncio
import requests
import json
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers
from proximityhash import create_geohash
import time
from ProjectConf.FirestoreConf import async_db, db


# Profile Id liked by user
def likes_given(userId=None, noOfLastRecords=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, childCollectionName=u'Given',
                                           matchFor="Likes", noOfLastRecords=noOfLastRecords)


# Profile Id super liked by user
def super_likes_given(userId=None, noOfLastRecords=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, childCollectionName=u'Given',
                                           matchFor="Superlikes", noOfLastRecords=noOfLastRecords)


# Profile Id dis-liked by user
def dislikes_given(userId=None, noOfLastRecords=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, childCollectionName=u'Given',
                                           matchFor="Dislikes", noOfLastRecords=noOfLastRecords)


def likes_received(userId=None, noOfLastRecords=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId,
                                           childCollectionName=u'Received', matchFor="Likes", noOfLastRecords=noOfLastRecords)


# Profile Id dis-liked by user
def dislikes_received(userId=None, noOfLastRecords=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId,
                                           childCollectionName=u'Received', matchFor="Dislikes", noOfLastRecords=noOfLastRecords)


# Profile Id super liked by user
def super_likes_received(userId=None, noOfLastRecords=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId,
                                           childCollectionName=u'Received', matchFor="Superlikes", noOfLastRecords=noOfLastRecords)

# Get list of proile ids from a certain collection
def get_profiles_from_subcollection(collectionName=None, userId=None, childCollectionName=None, matchFor=None, noOfLastRecords=None):
    try:
        request_body = {
            "currentUserId": userId,
            "childCollectionName": childCollectionName,
            "matchFor": matchFor,
            "noOfLastRecords": noOfLastRecords
        }
        profiles_array = requests.get(f"{cachingServerRoute}/getlikesdislikesforuser",
                                            data=json.dumps(request_body),
                                            headers=headers)
        return profiles_array.json()
    except Exception as e:
        print(traceback.format_exc())



def elite_picks(userId=None, noOfLastRecords=None):
    try:
        profile_ref = db.collection('ProfilesGrading')
        query = profile_ref.order_by("totalScore").limit_to_last(noOfLastRecords)
        docs = query.get()
        user_ids = [doc.id for doc in docs]
        request_body = {
            "profileIdList": user_ids
        }
        profiles_array = requests.get(f"{cachingServerRoute}/getprofilesbyids",
                                            data=json.dumps(request_body),
                                            headers=headers)
        profiles_array = profiles_array.json()
        return profiles_array
    except Exception as e:
        print(traceback.format_exc())
