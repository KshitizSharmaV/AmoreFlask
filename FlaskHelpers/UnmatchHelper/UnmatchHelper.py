import time
import asyncio
from ProjectConf.LoggerConf import logger
from FlaskHelpers.FirestoreFunctions import unmatch_task_likes_dislikes, unmatch_task_recent_chats


async def unmatch_task_function(current_user_id, other_user_id):
    """
    Asynchronously performs following firestore tasks:
        - Query firestore for current_user_id's match record for the other_user_id and fetch it.
        - Delete the above record from firestore.
        - Set the data from above record in Unmatch subcollection of current_user.
        - Delete the RecentChats record of other_user from the current_user's records and vice-versa.
    :param current_user_id: Current User's UID
    :param other_user_id: Other User's UID
    :return:
    """
    task_likes_dislikes_current_user = asyncio.create_task(unmatch_task_likes_dislikes(current_user_id, other_user_id))
    task_likes_dislikes_other_user = asyncio.create_task(unmatch_task_likes_dislikes(other_user_id, current_user_id))
    # Can be modified to show unmatched chats/chat listings in a more sophisticated manner.
    task_recent_chats_current_user = asyncio.create_task(unmatch_task_recent_chats(current_user_id, other_user_id))
    task_recent_chats_other_user = asyncio.create_task(unmatch_task_recent_chats(other_user_id, current_user_id))
    return await asyncio.gather(
        *[task_likes_dislikes_current_user, task_likes_dislikes_other_user, task_recent_chats_current_user,
          task_recent_chats_other_user])


# Production function used in API for geohash querying
def unmatch_production_function(current_user_id, other_user_id):
    start = time.time()
    results = asyncio.run(unmatch_task_function(current_user_id, other_user_id))
    results = list(results)
    logger.info(f"Successfully unmatched {other_user_id} from {current_user_id}'s matches.")
    print(f"Time Elapsed: {time.time() - start}")
    return results


# Invoke this function to test geohash querying
def unmatch_test_function(current_user_id, other_user_id):
    start = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(unmatch_task_function(current_user_id, other_user_id))
    results = loop.run_until_complete(future)
    print(f"Time Elapsed: {time.time() - start}")
    return results
