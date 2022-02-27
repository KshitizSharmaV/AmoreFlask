#################################################
###### Engine : Matching Engine
# Trigger this file to run Matching engine
#################################################
import os
import threading
import traceback
import time
import logging
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth
from logging.handlers import TimedRotatingFileHandler

# Firestore connection
cred = credentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

# Log Settings
LOG_FILENAME = datetime.now().strftime("%H_%M_%d_%m_%Y")+".log"
if not os.path.exists('Logs/MatchingEngine/'):
    os.makedirs('Logs/MatchingEngine/')
logHandler = TimedRotatingFileHandler(f'Logs/MatchingEngine/{LOG_FILENAME}',when="midnight")
logFormatter = logging.Formatter(f'%(asctime)s %(levelname)s %(threadName)s : %(message)s')
logHandler.setFormatter( logFormatter )
logger = logging.getLogger(f'Logs/MatchingEngine/{LOG_FILENAME}')
logger.addHandler( logHandler )
logger.setLevel( logging.INFO )

# logic to check the match between the 2 users
def calculate_the_match(firstUserSwipe=None,secondUserSwipe=None):
    try:
        if firstUserSwipe == "Likes":
            if secondUserSwipe == "Likes": return "Match"
            if secondUserSwipe == "Superlikes": return "Match"
            if secondUserSwipe == "Dislikes": return "NoMatch"
        elif firstUserSwipe == "Superlikes":
            if secondUserSwipe == "Like": return "Match"
            if secondUserSwipe == "Dislikes": return "NoMatch"
            if secondUserSwipe == "Superlikes": return "Match"
        elif firstUserSwipe == "Dislikes":
            if secondUserSwipe == "Superlikes": return "NoMatch"
            if secondUserSwipe == "Likes": return "NoMatch"
            if secondUserSwipe == "Dislikes": return "NoMatch"
    except Exception as e:
        logger.error(traceback.format_exc())
        return False               


# When a user swipes the LikesDislikes collection is updated, the listener listens to update and calls this function
# for the user who just swiped, send the id of user who just swiped to function check_the_match
def check_the_subcollection_for_matches(giverId=None):
    # we fetch only the newSwipes by Checking if matchVerified is not True
    newSwipes = db.collection("LikesDislikes").document(giverId).collection("Given").where(u'matchVerified', u'==', False).stream()
    for swipe in newSwipes:
        # Get the id of user who received the swipe
        receiverId = swipe.id
        # Data of user who gave the swipe
        giverSwipeData = swipe.to_dict()
        # Get the doc for user who received the swipe
        receiverSwipeDataDoc =  db.collection("LikesDislikes").document(receiverId).collection("Given").document(giverId).get()
        receiverSwipeData = receiverSwipeDataDoc.to_dict()
        # check if receiverSwipeData is None
        # if below condition is true that means this is second swipe. that means both users have swiped on each other
        # else this was the first swipe
        if receiverSwipeData:
            # find the match between two users
            match = calculate_the_match(firstUserSwipe=receiverSwipeData["swipe"],
                                        secondUserSwipe=giverSwipeData["swipe"])
            # both users swiped on each other
            logger.info(f'{match}: {giverId} and {receiverId} both swiped on each other')
            # write the match to firebase
            if match == 'Match':
                print("Match Encountered")
                print(f'{match}: {giverId} and {receiverId} both swiped on each other')
                db.collection("LikesDislikes").document(receiverId).collection("Match").document(giverId).set({"id": giverId, "timestamp": time.time()})
                db.collection("LikesDislikes").document(giverId).collection("Match").document(receiverId).set({"id": receiverId, "timestamp": time.time()})
                giver_profile = db.collection("Profiles").document(giverId).get().to_dict()
                receiver_profile = db.collection("Profiles").document(receiverId).get().to_dict()
                db.collection("RecentChats").document(receiverId).collection("Messages").document(giverId).set({"fromId": receiverId, "toId": giverId, 
                "timestamp": datetime.now(), "lastText": "", "user": {"firstName": giver_profile["firstName"], "lastName": giver_profile["lastName"], 
                "image1": giver_profile["image1"], "id": giverId}})
                db.collection("RecentChats").document(giverId).collection("Messages").document(receiverId).set({"fromId": giverId, "toId": receiverId, 
                "timestamp": datetime.now(), "lastText": "", "user": {"firstName": receiver_profile["firstName"], "lastName": receiver_profile["lastName"], 
                "image1": receiver_profile["image1"], "id": receiverId}})
            # db.collection(u'MatchingEngine').add({"firstUserId":receiverId,
            #     "secondUserId":giverId,
            #     "firstUserSwipe":receiverSwipeData["swipe"],
            #     "secondUserSwipe":giverSwipeData["swipe"],
            #     "firstUserNotified":False,
            #     "secondUserNotified":False,
            #     "timestsamp":time.time(),
            #     "matchingInfo":match
            # })
        else:
            # first swipe, wait for the second user to swipe too
            logger.info(f'{giverId} waiting on {receiverId} to swipe')
        # set the matchVerified = True, because we have processed this new swipe
        db.collection("LikesDislikes").document(giverId).collection("Given").document(receiverId).update({'matchVerified':True})
    # set the wasUpdated = False, because we processed the change
    db.collection("LikesDislikes").document(giverId).update({'wasUpdated':False})

    
# here each change that is listened to is processed
# each change can be of 3 types Added, Modified or Removed, these are 3 properties of firebase itself
# we only want to action when a new swipe was made
# TODO - We also want to consider what happens when a swipe is modified, what if a user upgrades or remove the like or dislike
def match_the_swipe(change=None):
    try:
        if change.type.name == 'ADDED':
            #logger.info(f'{change.document.id} added ')
            _ = check_the_subcollection_for_matches(giverId=change.document.id)
        elif change.type.name == 'MODIFIED':
            logger.info(f'{change.document.id} modified')
        elif change.type.name == 'REMOVED':
            #logger.info(f'{change.document.id} removed')
            pass
    except Exception as e:
        logger.error("Error occrured while processing the new swipe")
        logger.error(traceback.format_exc())
        return False               

# this function will be called every time firebase hears a change on a document in LikesDislikes
def matching_engine_listener(col_snapshot, changes, read_time):
    _ = [match_the_swipe(change=change) for change in changes]

def matching_engine_trigger():
    try:
        logger.info("Matching Engine Triggered")
        # Query the documents inside LikesDislikes collection where wasUpdated == true
        # if wasUpdated == true that means the user gave a new like/dislike/superlike
        col_query = db.collection(u'LikesDislikes').where(u'wasUpdated', '==', True)
        # Watch the collection query
        query_watch = col_query.on_snapshot(matching_engine_listener)
    except Exception as e:
        logger.error("Error occured in triggering matching engine")
        logger.error(traceback.format_exc())
        logger.warning("Un-suscribed from Matching Engine")
        return False               
    # Unsuscribe from all the listeners
    # query_watch.unsubscribe()

callback_done = threading.Event()
if __name__ == '__main__':
    matching_engine_trigger()
    while True:
        time.sleep(1)
    callback_done.set()