import time
import asyncio
from ProjectConf.FirestoreConf import db, async_db


async def was_updated_task(current_user_id):
    await async_db.collection('LikesDislikes').document(current_user_id).set({"wasUpdated": True})


async def given_swipe_task(current_user_id, swiped_user_id, swipe_info):
    await async_db.collection('LikesDislikes').document(current_user_id).collection("Given").document(
        swiped_user_id).set(
        {"swipe": swipe_info, "timestamp": time.time(), 'matchVerified': False})


async def received_swipe_task(current_user_id, swiped_user_id, swipe_info):
    await async_db.collection('LikesDislikes').document(swiped_user_id).collection("Received").document(
        current_user_id).set(
        {"swipe": swipe_info, "timestamp": time.time()})


async def swipe_tasks_future(current_user_id, swiped_user_id, swipe_info):
    task1 = asyncio.create_task(was_updated_task(current_user_id))
    task2 = asyncio.create_task(given_swipe_task(current_user_id, swiped_user_id, swipe_info))
    task3 = asyncio.create_task(received_swipe_task(current_user_id, swiped_user_id, swipe_info))
    return asyncio.gather(*[task1, task2, task3])


async def unmatch_task_likes_dislikes(user_id_1, user_id_2):
    match_ref = async_db.collection('LikesDislikes').document(user_id_1).collection("Match").document(user_id_2)
    match_doc = await match_ref.get()
    if match_doc.exists:
        match_doc = match_doc.to_dict()
        await match_ref.delete()
        unmatch_ref = async_db.collection('LikesDislikes').document(user_id_1).collection("Unmatch").document(user_id_2)
        await unmatch_ref.set(match_doc)


async def unmatch_task_recent_chats(user_id_1, user_id_2):
    recent_chat_ref = async_db.collection('RecentChats').document(user_id_1).collection("Messages").document(user_id_2)
    await recent_chat_ref.delete()



