from flask import jsonify, json

# Recommendation system 
# This will get the profiles for the swipe views 
class FetchProfiles(object):
    
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger

    def getProfiles(self, userId=None):
        profile_ref = self.db.collection(u'Profiles')
        docs = profile_ref.stream()
        # List of ids already seen by user
        idsAlreadySeenByUser = self.profilesAlreadySeenByUser(userId=userId)
        profilesArray = []
        for doc in docs:
            doctemp = doc.to_dict()
            if doc.id not in idsAlreadySeenByUser:
                doctemp["id"] = doc.id # un-comment for production
                profilesArray.append(doctemp)
        self.logger.info("Successfully sent back profiles for card swipe view")
        return jsonify(profilesArray)

    def profilesAlreadySeenByUser(self, userId=None):
        idsAlreadySeenByUser = (self.likedProfilesByUser(userId=userId) + 
                            self.superLikedProfilesByUser(userId=userId) + 
                            self.dislikedProfilesByUser(userId=userId))
        return idsAlreadySeenByUser

    def likedProfilesByUser(self, userId=None):
        return self.getProfileIds(collectionName=u'LikesDislikes',
                            userId=userId,
                            collectionNameChild=u'Likes')
    
    def superLikedProfilesByUser(self, userId=None):
        return self.getProfileIds(collectionName=u'LikesDislikes',
                            userId=userId,
                            collectionNameChild=u'SuperLikes')

    def dislikedProfilesByUser(self, userId=None):
        return self.getProfileIds(collectionName=u'LikesDislikes',
                            userId=userId,
                            collectionNameChild=u'Dislikes')

    def profilesWhoLikedUser(self):
        pass

    def getProfileIds(self, collectionName=None, userId=None, collectionNameChild=None):
        collection_ref = self.db.collection(collectionName)
        collection_ref_likedislike_userIds = collection_ref.document(userId)
        collection_ref_second_child = collection_ref_likedislike_userIds.collection(collectionNameChild)
        docs = collection_ref_second_child.stream()
        userIds = []
        _ = [userIds.append(doc.to_dict()['id']) for doc in docs]
        return userIds
    
