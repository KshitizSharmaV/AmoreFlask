# Profiles Fetcher
# This will get the profiles for the swipe views
from logging import exception
import time

from ProjectConf.FirestoreConf import db, async_db
from ProjectConf.LoggerConf import logger
from ProximityHash.proximityhash import *
import asyncio
import traceback
import itertools
from google.cloud import firestore

def getProfiles(userId=None, idsAlreadyInDeck=None):
    profile_ref = db.collection(u'Profiles')
    docs = profile_ref.stream()
    # List of ids already seen by user
    idsAlreadySeenByUser = profilesAlreadySeenByUser(userId=userId)
    allIdsToBeExcluded = idsAlreadySeenByUser + idsAlreadyInDeck
    profilesArray = []
    for doc in docs:
        doctemp = doc.to_dict()
        if doc.id not in allIdsToBeExcluded:
            doctemp["id"] = doc.id  # un-comment for production
            profilesArray.append(doctemp)
    logger.info("Successfully sent back profiles for card swipe view")
    return profilesArray

'''
2. Send user card deck list from client and set(idsAlreadySeenByUser+inDeck)
3. Caching - to be investigated further - Basic functionality functioning before - new cache for every server?
'''

# Caching ? - Next Stage
def profilesAlreadySeenByUser(userId=None):
    idsAlreadySeenByUser = []
    collection_ref = db.collection('LikesDislikes').document(userId).collections()
    for collection in collection_ref:
        for doc in collection.stream():
            idsAlreadySeenByUser.append(doc.to_dict()['id'])
    return idsAlreadySeenByUser


####################################
# Non-async functions. Flask can't make use of async function while processing requests. The async functioanlity is being 
# hence forth depployed on WSGI server which creates a thread for every request. GUNICON incase of flask i.e. how it communicates
# betwee a server and a flask application - KTZ
####################################
# Profile Id liked by user
def likesGiven(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, collectionNameChild=u'Likes')
# Profile Id superliked by user
def superLikesGiven(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, collectionNameChild=u'Superlikes')
# Profilee Id dis-liked by user
def dislikesGiven(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, collectionNameChild=u'Dislikes')
def likesReceived(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId,collectionNameChild=u'LikedBy')
# Profile Id superliked by user
def dislikesLikesReceived(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, collectionNameChild=u'DislikedBy')
# Profilee Id dis-liked by user
def superLikesReceived(userId=None):
    return get_profiles_from_subcollection(collectionName=u'LikesDislikes', userId=userId, collectionNameChild=u'SuperlikedBy')
def elitePicks(userId=None):
    try:
        profile_ref = db.collection('ProfilesGrading')
        query = profile_ref.order_by("totalScore").limit_to_last(10)
        docs = query.get()
        userIds = []
        for doc in docs:
            temp = doc.to_dict()
            userIds.append(temp['id'])
        return userIds
    except Exception as e:
        print(traceback.format_exc())
    


####################################
# Async functions to be used internally for service jobs
####################################

# All Profiles which liked the user
async def profiles_which_liked_user(userId=None):
    return await async_get_profiles_from_subcollection(collectionName=u'LikesDislikes',userId=userId,collectionNameChild=u'LikedBy')
# All Profiles which superliked the user
async def profiles_which_superliked_user(userId=None):
    return await async_get_profiles_from_subcollection(collectionName=u'LikesDislikes',userId=userId,collectionNameChild=u'SuperlikedBy')
# All Profiles which disliked the user
async def profiles_which_disliked_user(userId=None):
    return await async_get_profiles_from_subcollection(collectionName=u'LikesDislikes',userId=userId,collectionNameChild=u'DislikedBy')

# Get Profiles of list of ids
def getProfilesForListOfIds(listofIds=None):
    profilesArray = []
    _ = [profilesArray.append(get_profile_for_id(profileId=id)) for id in listofIds]
    return profilesArray

# Get profile for a certain id 
async def async_get_profile_for_id(profileId=None):
    profile_ref = async_db.collection('Profiles')
    doc = await profile_ref.document(profileId).get()
    doctemp = doc.to_dict()
    doctemp["id"] = doc.id  # un-comment for production
    return doctemp

# Get list of proile ids from a certain collection
async def async_get_profiles_from_subcollection(collectionName=None, userId=None, collectionNameChild=None):
    collection_ref = async_db.collection(collectionName)
    collection_ref_likedislike_userIds = collection_ref.document(userId)
    collection_ref_second_child = collection_ref_likedislike_userIds.collection(collectionNameChild)
    docs = collection_ref_second_child.stream()
    userIds = [doc.to_dict()['id'] async for doc in docs]
    return userIds

# Get profile for a certain id
def get_profile_for_id(profileId=None):
    profile_ref = db.collection('Profiles')
    doc = profile_ref.document(profileId).get()
    doctemp = doc.to_dict()
    doctemp["id"] = doc.id  # un-comment for production
    return doctemp

# Get list of proile ids from a certain collection
def get_profiles_from_subcollection(collectionName=None, userId=None, collectionNameChild=None):
    try:
        collection_ref = db.collection(collectionName)
        collection_ref_likedislike_userIds = collection_ref.document(userId)
        collection_ref_second_child = collection_ref_likedislike_userIds.collection(collectionNameChild).order_by(u'timestamp', direction=firestore.Query.DESCENDING)
        docs = collection_ref_second_child.stream()
        userIds = [doc.to_dict()['id'] for doc in docs]
        return userIds
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
    # geohashes = create_geohash(latitude=latitude, longitude=longitude, radius=radius, precision=get_max_precision_level(radius/9),
    #                            georaptor_flag=True)
    geohashes = list(create_geohash(latitude=latitude, longitude=longitude, radius=radius*1000, precision=4,
                                georaptor_flag=True))
    print(geohashes)
    print(len(geohashes))
    return await asyncio.gather(*[get_profiles_within_geohash(geohash) for geohash in geohashes])
    # return await asyncio.gather(*[get_profiles_within_geohashes(geohashes[i:i+10]) for i in range(0, len(geohashes), 10)])

# Production function used in API for geohash querying
def get_profiles_within_radius(userId, idsAlreadyInDeck, latitude, longitude, radius):
    start = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(profiles_within_radius_tasks(latitude=latitude, longitude=longitude, radius=radius))
    profiles = loop.run_until_complete(future)
    # results = asyncio.run(profiles_within_radius_tasks(latitude=latitude, longitude=longitude, radius=radius))
    profiles = list(set(itertools.chain.from_iterable(profiles)))
    profiles = list(map(lambda x: x.to_dict(), profiles))
    # List of ids already seen by user
    idsAlreadySeenByUser = profilesAlreadySeenByUser(userId=userId)
    allIdsToBeExcluded = idsAlreadySeenByUser + idsAlreadyInDeck
    profilesArray = []
    for profile in profiles:
        profile_temp = profile.to_dict()
        if profile.id not in allIdsToBeExcluded:
            profile_temp["id"] = profile.id  # un-comment for production
            profilesArray.append(profile_temp)
    logger.info("Successfully sent back profiles for card swipe view")
    print(f"Time Elapsed: {time.time() - start}")
    return profilesArray

# Invoke this function to test geohash querying
def test_get_profiles_within_radius(latitude, longitude, radius):
    start = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(profiles_within_radius_tasks(latitude=latitude, longitude=longitude, radius=radius))
    profiles = loop.run_until_complete(future)
    # results = asyncio.run(profiles_within_radius_tasks(latitude=latitude, longitude=longitude, radius=radius))
    profiles = list(set(itertools.chain.from_iterable(profiles)))
    profiles = list(map(lambda x: x.to_dict(), profiles))
    print(f"Time Elapsed: {time.time() - start}")
    return profiles
