"""
How will u grade them :
- Grading by popularity. KPI LIkes, SuperLikes and Dislikes
- Profile Completeion 
- How the active user is 
- How responsive user is on messages 
- How many times a person have been reported
    - Nature of Offence
"""
import time
from Services.FetchProfiles import *
from ProjectConf.FirestoreConf import async_db
import asyncio

# total_score: float  # 0 to 10
# popularity_score: float  # 0 to 10
# profile_completion_score: float  # 0 to 10
# user_activity_score: float  # 0 to 10
# user_responsiveness_score: float  # 0 to 10
# user_offence_score: float  # will be in negative, 0 to -40


async def calculate_total_score(userId):
    popularity_score = await calculate_popularity_score(userId=userId)
    profile_completion_score = await get_profile_completion_score(userId=userId)
    total_score = popularity_score + profile_completion_score
    await store_profile_grading_firestore(userId=userId, total_score=total_score, popularity_score=popularity_score,
                                          profile_completion_score=profile_completion_score)
    print(f"profile popularity score for {userId}: {popularity_score}")
    print(f"profile completion score for {userId}: {profile_completion_score}")
    print(f"profile grading score for {userId}: {total_score}")
    print("__________________________________________________________________________________________")


async def calculate_popularity_score(userId):
    """
        superlike -- +4
        like -- +2
        dislike -- -1
        _______________
        561
        How to convert 561 to a score on 0-10 scale?
    """
    liked_by_list = await profiles_which_liked_user(userId=userId)
    disliked_by_list = await profiles_which_disliked_user(userId=userId)
    superliked_by_list = await profiles_which_superliked_user(userId=userId)
    return (4 * len(superliked_by_list)) + (2 * len(liked_by_list)) - len(disliked_by_list)


async def get_profile_completion_score(userId):
    profile = await async_get_profile_for_id(profileId=userId)
    return (float(profile['profileCompletion']) / 100) * 10


async def store_profile_grading_firestore(userId, total_score, popularity_score, profile_completion_score):
    try:
        timestamp = time.time()
        await async_db.collection('ProfilesGrading').document(userId).set({"totalScore": total_score, 
                                                                        "id":userId,
                                                                        "popularityScore": popularity_score,
                                                                        "profileCompletionScore": profile_completion_score, 
                                                                        "timestamp": timestamp})
        await async_db.collection('ProfilesGrading').document(userId).collection(userId).document(str(timestamp)).set({"totalScore": total_score, 
                                "id":userId,
                                "popularityScore": popularity_score,
                                 "profileCompletionScore": profile_completion_score,
                                 "timestamp": timestamp})
        print(f"Profile grading for {userId} stored successfully.")
    except Exception as e:
        print(f"Exception in storing profile grading for {userId}: {e}")


