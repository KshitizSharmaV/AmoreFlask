# Profiles Fetcher
# This will get the profiles for the swipe views
import time

from ProjectConf.FirestoreConf import db, async_db
from ProjectConf.LoggerConf import logger
from ProximityHash.proximityhash import *
import asyncio
import itertools


class FetchProfiles(object):

    def getProfiles(self, userId=None, idsAlreadyInDeck=None):
        profile_ref = db.collection(u'Profiles')
        docs = profile_ref.stream()
        # List of ids already seen by user
        idsAlreadySeenByUser = self.profilesAlreadySeenByUser(userId=userId)
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
    def profilesAlreadySeenByUser(self, userId=None):
        idsAlreadySeenByUser = []
        collection_ref = db.collection('LikesDislikes').document(userId).collections()
        for collection in collection_ref:
            for doc in collection.stream():
                idsAlreadySeenByUser.append(doc.to_dict()['id'])
        return idsAlreadySeenByUser

    # Profile Id liked by user
    def likedProfilesByUser(self, userId=None):
        return self.get_profiles_from_subcollection(collectionName=u'LikesDislikes',
                                                    userId=userId,
                                                    collectionNameChild=u'Likes')

    # Profile Id superliked by user
    def superLikedProfilesByUser(self, userId=None):
        return self.get_profiles_from_subcollection(collectionName=u'LikesDislikes',
                                                    userId=userId,
                                                    collectionNameChild=u'Superlikes')

    # Profilee Id dis-liked by user
    def dislikedProfilesByUser(self, userId=None):
        return self.get_profiles_from_subcollection(collectionName=u'LikesDislikes',
                                                    userId=userId,
                                                    collectionNameChild=u'Dislikes')

    # All Profiles which liked the user
    async def profiles_which_liked_user(self, userId=None):
        return await self.async_get_profiles_from_subcollection(collectionName=u'LikesDislikes',
                                                                userId=userId,
                                                                collectionNameChild=u'LikedBy')

    # All Profiles which superliked the user
    async def profiles_which_superliked_user(self, userId=None):
        return await self.async_get_profiles_from_subcollection(collectionName=u'LikesDislikes',
                                                                userId=userId,
                                                                collectionNameChild=u'SuperlikedBy')

    # All Profiles which disliked the user
    async def profiles_which_disliked_user(self, userId=None):
        return await self.async_get_profiles_from_subcollection(collectionName=u'LikesDislikes',
                                                                userId=userId,
                                                                collectionNameChild=u'DislikedBy')

    # Cached
    def superElitePicks(self):
        pass

    # Get Profiles of list of ids
    def getProfilesForListOfIds(self, listofIds=None):
        profilesArray = []
        _ = [profilesArray.append(self.get_profile_for_id(profileId=id)) for id in listofIds]
        return profilesArray

    # Get profile for a certain id 
    async def async_get_profile_for_id(self, profileId=None):
        profile_ref = async_db.collection('Profiles')
        doc = await profile_ref.document(profileId).get()
        doctemp = doc.to_dict()
        doctemp["id"] = doc.id  # un-comment for production
        return doctemp

    # Get list of proile ids from a certain collection
    async def async_get_profiles_from_subcollection(self, collectionName=None, userId=None, collectionNameChild=None):
        collection_ref = async_db.collection(collectionName)
        collection_ref_likedislike_userIds = collection_ref.document(userId)
        collection_ref_second_child = collection_ref_likedislike_userIds.collection(collectionNameChild)
        docs = collection_ref_second_child.stream()
        userIds = [doc.to_dict()['id'] async for doc in docs]
        return userIds

    # Get profile for a certain id
    def get_profile_for_id(self, profileId=None):
        profile_ref = db.collection('Profiles')
        doc = profile_ref.document(profileId).get()
        doctemp = doc.to_dict()
        doctemp["id"] = doc.id  # un-comment for production
        return doctemp

    # Get list of proile ids from a certain collection
    def get_profiles_from_subcollection(self, collectionName=None, userId=None, collectionNameChild=None):
        collection_ref = db.collection(collectionName)
        collection_ref_likedislike_userIds = collection_ref.document(userId)
        collection_ref_second_child = collection_ref_likedislike_userIds.collection(collectionNameChild)
        docs = collection_ref_second_child.stream()
        userIds = [doc.to_dict()['id'] for doc in docs]
        return userIds


def get_max_precision_level(radius):
    """
    Under implementation, not used anywhere currently.
    :param radius:
    :return:
    """
    if radius > 2500:
        return 1
    elif radius > 630:
        return 2
    elif radius > 78:
        return 3
    elif radius > 20:
        return 4
    elif radius > 2.5:
        return 5
    elif radius > 0.6:
        return 6
    elif radius > 0.07:
        return 7


async def get_profiles_within_geohash(geohash):
    colref = async_db.collection('FilterAndLocation')
    docs = colref.where("geohash.geohash", ">=", geohash)
    profiles = [doc.id async for doc in docs.stream()]
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
    geohashes = create_geohash(latitude=latitude, longitude=longitude, radius=radius, precision=10,
                               georaptor_flag=True, minlevel=3, maxlevel=7)
    print(geohashes)
    return await asyncio.gather(*[get_profiles_within_geohash(geohash) for geohash in geohashes])

# Invoke this function to test geohash querying
def get_profiles_within_radius(latitude, longitude, radius):
    start = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(profiles_within_radius_tasks(latitude=latitude, longitude=longitude, radius=radius))
    results = loop.run_until_complete(future)
    # results = asyncio.run(profiles_within_radius_tasks(latitude=latitude, longitude=longitude, radius=radius))
    results = list(set(itertools.chain.from_iterable(results)))
    print(f"Time Elapsed: {time.time() - start}")
    return results
