# from flask import jsonify, json

# # Recommendation system 
# # This will get the profiles for the swipe views 
# # Profile will come twice 

# class FetchProfiles(object):
    
#     def __init__(self, db, logger):
#         self.db = db
#         self.logger = logger

#     # Mechanism in 
#     def getProfiles(self, userId=None, numberOfCards=30):

#         alreadySeen = 100
#         60/100
#         UniverseSize = 10000

#         # Add filter

#         profile_ref = self.db.collection(u'Profiles').set_limit(numberOfCards)
#         docs = profile_ref.stream()
#         # List of ids already seen by user
#         # Caching - over here
#         idsAlreadySeenByUser = self.profilesAlreadySeenByUser(userId=userId)
#         profilesArray = []
#         for doc in docs:
#             doctemp = doc.to_dict()
#             # What should happen if (numberOfCards-)
#             if doc.id not in idsAlreadySeenByUser:
#                 doctemp["id"] = doc.id # un-comment for production
#                 profilesArray.append(doctemp)
#             else:
#                 seenProfiles +=1
#                 if seenProfile >= 15:
#                     return Array 
#                 else:
#                     self.getProfileIds(numberOfCards=numberOfCards-seenProfiles)
#                 self.getProfileIds(numberOfCards=numberOfCards-seenProfiles)
#         self.logger.info("Successfully sent back profiles for card swipe view")
#         return jsonify(profilesArray)

#     '''
#     1. Fetch all collection from LikesDisklikes rather than muliple sound trips
#     '''

#     def profilesAlreadySeenByUser(self, userId=None):
#         idsAlreadySeenByUser = (self.likedProfilesByUser(userId=userId) + 
#                             self.superLikedProfilesByUser(userId=userId) + 
#                             self.dislikedProfilesByUser(userId=userId))
#         return idsAlreadySeenByUser

#     def likedProfilesByUser(self, userId=None):
#         return self.getProfileIds(collectionName=u'LikesDislikes',
#                             userId=userId,
#                             collectionNameChild=u'Likes')
    
#     def superLikedProfilesByUser(self, userId=None):
#         return self.getProfileIds(collectionName=u'LikesDislikes',
#                             userId=userId,
#                             collectionNameChild=u'SuperLikes')

#     def dislikedProfilesByUser(self, userId=None):
#         return self.getProfileIds(collectionName=u'LikesDislikes',
#                             userId=userId,
#                             collectionNameChild=u'Dislikes')

#     def profilesWhoLikedUser(self):
#         pass

#     def getProfileIds(self, collectionName=None, userId=None, collectionNameChild=None):
#         collection_ref = self.db.collection(collectionName)
#         collection_ref_likedislike_userIds = collection_ref.document(userId)
#         collection_ref_second_child = collection_ref_likedislike_userIds.collection(collectionNameChild)
#         docs = collection_ref_second_child.stream()
#         userIds = []
#         _ = [userIds.append(doc.to_dict()['id']) for doc in docs]
#         return userIds
    
