# Matching Engine
# Use this class to invoke sub classes in Matching engine 
from ProjectConf.FirestoreConf import db, async_db
import traceback

def store_matches(firstUserId=None, secondUserId=None, firstUserSwipe=None, secondUserSwipe=None, firstUserNotified=None, secondUserNotified=None, timestsamp=None):
    try:
        print("store_matches %s %s" %(firstUserId, secondUserId))
        data = {"firstUserId":firstUserId,
                "secondUserId":secondUserId,
                "firstUserSwipe":firstUserSwipe,
                "secondUserSwipe":secondUserSwipe,
                "firstUserNotified":firstUserNotified,
                "timestsamp":timestsamp
            }
        db.collection(u'MatchingEngine').add(data)
        return True
    except Exception as e:
        print(traceback.format_exc())        
        print(e)   
        return False     




