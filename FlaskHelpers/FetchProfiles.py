# Profiles Fetcher
# This will get the profiles for the swipe views
import profile
import traceback
import itertools
import asyncio
import requests
import json
from ProjectConf.ReadFlaskYaml import cachingServerRoute, headers
from google.cloud import firestore
from ProjectConf.LoggerConf import logger
from ProximityHash.proximityhash import *
from ProjectConf.FirestoreConf import async_db, db

'''
2. Send user card deck list from client and set(idsAlreadySeenByUser+inDeck)
3. Caching - to be investigated further - Basic functionality functioning before - new cache for every server?
'''

"""
Implemented in Amore Caching Service
"""


def get_profiles(user_id=None, ids_already_in_deck=None):
    """
    Get all profiles from Cache
    """
    # profile_ref = db.collection(u'Profiles')
    # query = profile_ref.order_by("age").limit_to_last(50)
    # docs = query.get()
    request_body = {
        "cacheFilterName": "Profiles*"
    }
    all_profiles_response = requests.get(f"{cachingServerRoute}/getallcachedprofiles",
                                         data=json.dumps(request_body),
                                         headers=headers)
    # all_profiles = json.loads(all_profiles_response)
    all_profiles = all_profiles_response.json()
    all_profiles = (json.loads(profile) for profile in all_profiles)
    """
    Get List of ids already seen by user from cache
    """
    ids_already_seen_by_user = profiles_already_seen_by_user(user_id=user_id)
    all_ids_to_be_excluded = ids_already_seen_by_user + ids_already_in_deck
    profiles_array = [{"id": profile["id"], **profile} for profile in all_profiles if
                      profile["id"] not in all_ids_to_be_excluded]
    logger.info("Successfully sent back profiles for card swipe view")
    return profiles_array


# Caching ? - Next Stage
def profiles_already_seen_by_user(user_id=None):
    """
    Get list of ids already seen by user from cache
    """
    request_data = {
        'currentUserId': user_id
    }
    ids_already_seen_by_user_response = requests.post(f"{cachingServerRoute}/getprofilesalreadyseen",
                                                      data=json.dumps(request_data),
                                                      headers=headers)
    ids_already_seen_by_user = ids_already_seen_by_user_response.json()
    ids_already_seen_by_user = list(ids_already_seen_by_user) if not isinstance(ids_already_seen_by_user, list) \
        else ids_already_seen_by_user
    return ids_already_seen_by_user


"""
Functions yet to be ported to Amore Caching Server
"""


####################################
# Non-async functions. Flask can't make use of async function while processing requests. The async functioanlity is being 
# hence forth depployed on WSGI server which creates a thread for every request. GUNICON incase of flask i.e. how it communicates
# betwee a server and a flask application - KTZ
####################################
# Profile Id liked by user
def likes_given(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, collectionNameChild=u'Given',
                                           matchFor="Likes")


# Profile Id super liked by user
def super_likes_given(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, collectionNameChild=u'Given',
                                           matchFor="Superlikes")


# Profile Id dis-liked by user
def dislikes_given(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, collectionNameChild=u'Given',
                                           matchFor="Dislikes")


def likes_received(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId,
                                           collectionNameChild=u'Received', matchFor="Likes")


# Profile Id dis-liked by user
def dislikes_received(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId,
                                           collectionNameChild=u'Received', matchFor="Dislikes")


# Profile Id super liked by user
def super_likes_received(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId,
                                           collectionNameChild=u'Received', matchFor="Superlikes")


def elite_picks(userId=None):
    try:
        profile_ref = db.collection('ProfilesGrading')
        query = profile_ref.order_by("totalScore").limit_to_last(10)
        docs = query.get()
        user_ids = [doc.id for doc in docs]
        return user_ids
    except Exception as e:
        print(traceback.format_exc())


# Get Profiles of list of ids
async def get_profiles_for_list_of_ids(list_of_ids=None):
    profilesArray = await asyncio.gather(*[get_profile_for_id(profile_id=id) for id in list_of_ids])
    return profilesArray


# Get profile for a certain id
async def get_profile_for_id(profile_id=None):
    profile_ref = async_db.collection('Profiles')
    doc = await profile_ref.document(profile_id).get()
    doc_temp = doc.to_dict()
    doc_temp["id"] = doc.id  # un-comment for production
    return doc_temp


# Get list of proile ids from a certain collection
def get_profiles_from_subcollection(collectionName=None, userId=None, collectionNameChild=None, matchFor=None):
    try:
        docs = db.collection(collectionName).document(userId).collection(collectionNameChild).where(u'swipe', u'==',
                                                                                                    matchFor).order_by(
            u'timestamp', direction=firestore.Query.DESCENDING).stream()
        user_ids = [doc.id for doc in docs]
        return user_ids
    except Exception as e:
        print(traceback.format_exc())


async def get_profiles_within_geohash(geohash):
    colref = async_db.collection('FilterAndLocation')
    if len(geohash) == 2:
        docs = colref.where("geohash2", "==", geohash)
        print("geo2 triggered...")
    elif len(geohash) == 3:
        docs = colref.where("geohash3", "==", geohash)
        print("geo3 triggered...")
    elif len(geohash) == 4:
        docs = colref.where("geohash4", "==", geohash)
        print("geo4 triggered...")
    elif len(geohash) == 5:
        docs = colref.where("geohash5", "==", geohash)
        print("geo5 triggered...")
    else:
        print("Else part triggered...")
        docs = colref.where("geohash", ">=", geohash).where('geohash', '<=', geohash + '\uf8ff')
    profiles = [doc async for doc in docs.stream()]
    return profiles


async def profiles_within_radius_tasks(latitude, longitude, radius):
    """
    Asynchronously query firestore for user ids that are within a given radius of user location
    create_geohash() method defined in ProximityHash/proximityhash.py
    create_geohash(): computes and gives Set of unique geohashes in the given radius from given lat/long.
    Georaptor ensures minimum number of geohashes are produced to define the search area.
    :param latitude:
    :param longitude:
    :param radius:
    :return: Query results from firestore (user IDs)
    """
    geohashes = list(create_geohash(latitude=latitude, longitude=longitude, radius=radius * 1000, precision=4,
                                    georaptor_flag=True))
    print(geohashes)
    print(len(geohashes))
    return await asyncio.gather(*[get_profiles_within_geohash(geohash) for geohash in geohashes])


# Production function used in API for geohash querying
def get_profiles_within_radius(userId, ids_already_in_deck, latitude, longitude, radius):
    start = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(profiles_within_radius_tasks(latitude=latitude, longitude=longitude, radius=radius))
    profiles = loop.run_until_complete(future)
    # results = asyncio.run(profiles_within_radius_tasks(latitude=latitude, longitude=longitude, radius=radius))
    profiles = list(set(itertools.chain.from_iterable(profiles)))
    profiles = list(map(lambda x: x.to_dict(), profiles))
    # List of ids already seen by user
    ids_already_seen_by_user = profiles_already_seen_by_user(user_id=userId)
    all_ids_to_be_excluded = ids_already_seen_by_user + ids_already_in_deck
    profiles_array = [{"id": profile.id, **profile.to_dict()} for profile in profiles if
                      profile.id not in all_ids_to_be_excluded]
    logger.info("Successfully sent back profiles for card swipe view")
    print(f"Time Elapsed: {time.time() - start}")
    return profiles_array


# Invoke this function to test geohash querying
def test_get_profiles_within_radius(latitude, longitude, radius):
    start = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(profiles_within_radius_tasks(latitude=latitude, longitude=longitude, radius=radius))
    profiles = loop.run_until_complete(future)
    profiles = list(set(itertools.chain.from_iterable(profiles)))
    profiles = list(map(lambda x: x.to_dict(), profiles))
    print(f"Time Elapsed: {time.time() - start}")
    return profiles
