from MatchingEngine.MainMatchingEngine import store_matches
import traceback

def swipe_view_connector(current_user_id=None, swiped_user_id=None):
    try:
        print("swipe_view_connector %s %s" %(current_user_id, swiped_user_id))
        successStorage = store_matches(firstUserId = current_user_id, 
                        secondUserId = swiped_user_id,
                        firstUserSwipe = "SuperLike", 
                        secondUserSwipe = "like", 
                        firstUserNotified = False, 
                        secondUserNotified = False, 
                        timestsamp = False)
        
        # if successfully stored
        if successStorage :
            return True
        else:
            return False
    except Exception as e:
        print(traceback.format_exc())        
        print(e)   
        return False     
