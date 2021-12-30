
from ProjectConf.FirestoreConf import db, async_db
import traceback
from MatchingEngine.MainMatchingEngine import calculate_the_match

def store_matches(firstUserId=None, secondUserId=None, firstUserSwipe=None, secondUserSwipe=None, firstUserNotified=None, secondUserNotified=None, timestsamp=None):
    try:
        print("store_matches %s %s" %(firstUserId, secondUserId))

        # calculate the outcome of matching the profiles
        matchOutcome = calculate_the_match(firstUserSwipe=firstUserSwipe,secondUserSwipe=secondUserSwipe)
        data = {"firstUserId":firstUserId,
                "secondUserId":secondUserId,
                "firstUserSwipe":firstUserSwipe,
                "secondUserSwipe":secondUserSwipe,
                "firstUserNotified":firstUserNotified,
                "timestsamp":timestsamp,
                "matchingInfo":matchOutcome
            }
        db.collection(u'MatchingEngine').add(data)
        return True
        
    except Exception as e:
        print(traceback.format_exc())        
        print(e)   
        return False     

