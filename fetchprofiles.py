# Profiles Fetcher
# This will get the profiles for the swipe views 
class FetchProfiles(object):
    
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger

    def getProfiles(self, userId=None, idsAlreadyInDeck=None):
        profile_ref = self.db.collection(u'Profiles')
        docs = profile_ref.stream()
        # List of ids already seen by user
        idsAlreadySeenByUser = self.profilesAlreadySeenByUser(userId=userId)
        allIdsToBeExcluded =  idsAlreadySeenByUser + idsAlreadyInDeck
        profilesArray = []
        for doc in docs:
            doctemp = doc.to_dict()
            if doc.id not in allIdsToBeExcluded:
                doctemp["id"] = doc.id # un-comment for production
                profilesArray.append(doctemp)
        self.logger.info("Successfully sent back profiles for card swipe view")
        return profilesArray

    '''
    2. Send user card deck list from client and set(idsAlreadySeenByUser+inDeck)
    3. Caching - to be investigated further - Basic functionality functioning before - new cache for every server?
    '''

    # Caching ? - Next Stage
    def profilesAlreadySeenByUser(self, userId=None):
        idsAlreadySeenByUser = []
        collection_ref = self.db.collection('LikesDislikes').document(userId).collections()
        for collection in collection_ref:
            for doc in collection.stream():
                idsAlreadySeenByUser.append(doc.to_dict()['id'])
        return idsAlreadySeenByUser

    # Profile Id liked by user
    def likedProfilesByUser(self, userId=None):
        return self.getProfileIds(collectionName=u'LikesDislikes',
                            userId=userId,
                            collectionNameChild=u'Likes')
    
    # Profile Id superliked by user
    def superLikedProfilesByUser(self, userId=None):
        return self.getProfileIds(collectionName=u'LikesDislikes',
                            userId=userId,
                            collectionNameChild=u'Superlikes')

    # Profilee Id dis-liked by user
    def dislikedProfilesByUser(self, userId=None):
        return self.getProfileIds(collectionName=u'LikesDislikes',
                            userId=userId,
                            collectionNameChild=u'Dislikes')

    # All Profiles who liked the user
    def profilesWhoLikedUser(self):
        pass
    
    # Cached
    def superElitePicks(self):
        pass

    # Get Profiles of list of ids
    def getProfilesForListOfIds(self, listofIds=None):
        profilesArray = []
        _ = [profilesArray.append(self.getProfileForId(profileId=id)) for id in listofIds]
        return profilesArray

    # Get profile for a certain id 
    def getProfileForId(self, profileId=None):
        profile_ref = self.db.collection(u'Profiles')
        doc = profile_ref.document(profileId).get()
        doctemp = doc.to_dict()
        doctemp["id"] = doc.id # un-comment for production
        return doctemp

    # Get list of proile ids from a certain collection
    def getProfileIds(self, collectionName=None, userId=None, collectionNameChild=None):
        collection_ref = self.db.collection(collectionName)
        collection_ref_likedislike_userIds = collection_ref.document(userId)
        collection_ref_second_child = collection_ref_likedislike_userIds.collection(collectionNameChild)
        docs = collection_ref_second_child.stream()
        userIds = []
        _ = [userIds.append(doc.to_dict()['id']) for doc in docs]
        return userIds
    
