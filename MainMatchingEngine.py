# Trigger this file to run Matching engine
# Matching Engine starts from here

import threading
import traceback
import time
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from ProjectConf.FirestoreConf import async_db, db

LOG_FILENAME = datetime.now().strftime("%H_%M_%d_%m_%Y")+".log"
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
        receiverSwipeDataDoc =  db.collection("LikesDislikes").document(receiverId).collection("Given").document(receiverId).get()
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
            db.collection(u'MatchingEngine').add({"firstUserId":receiverId,
                "secondUserId":giverId,
                "firstUserSwipe":receiverSwipeData["swipe"],
                "secondUserSwipe":giverSwipeData["swipe"],
                "firstUserNotified":False,
                "secondUserNotified":False,
                "timestsamp":time.time(),
                "matchingInfo":match
            })
        else:
            # first swipe, wait for the second user to swipe too
            logger.info(f'{giverId} waiting on {receiverId} to swipe')
        # set the matchVerified = True, because we have processed this new swipe
        db.collection("LikesDislikes").document(giverId).collection("Given").document(receiverId).update({'matchVerified':True})
    
# here each change that is listened to is processed
def match_the_swipe(change=None):
    try:
        logger.error("##############")
        if change.type.name == 'ADDED':
            logger.info(f'{change.document.id} added ')
            _ = check_the_subcollection_for_matches(giverId=change.document.id)
        elif change.type.name == 'MODIFIED':
            logger.info(f'{change.document.id} modified')
        elif change.type.name == 'REMOVED':
            logger.info(f'{change.document.id} removed')
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
        logger.warning("Un-suscribed from all Matching Engine")
        return False               
    # Unsuscribe from all the listeners
    # query_watch.unsubscribe()

if __name__ == '__main__':
    callback_done = threading.Event()
    matching_engine_trigger()
    while True:
        time.sleep(1)
    callback_done.set()