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
import pandas as pd
import random


# total_score: float  # 0 to 10
# popularity_score: float  # 0 to 10
# profile_completion_score: float  # 0 to 10
# user_activity_score: float  # 0 to 10
# user_responsiveness_score: float  # 0 to 10
# user_offence_score: float  # will be in negative, 0 to -40

async def calculate_total_score(userId):
    popularity_score = await calculate_popularity_score(userId=userId)
    profile_completion_score = await get_profile_completion_score(userId=userId)
    activity_score = await calculate_activity_score(userId=userId)
    matching_score  = await calculate_matching_score(userId=userId)
    all_profile_scores = {"userId":userId,
                        "popularity_score":popularity_score,
                        "profile_completion_score":profile_completion_score,
                        "activity_score":activity_score,
                        "matching_score":matching_score}
    return all_profile_scores
    print(f"profile popularity score for {userId}: {popularity_score}")
    print(f"profile completion score for {userId}: {profile_completion_score}")
    print(f"profile grading score for {userId}: {total_score}")
    print("__________________________________________________________________________________________")

# popularity score is calculated based on number of super likes, likes & dislike received
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

# how much of profile has user completed
async def get_profile_completion_score(userId):
    profile = await async_get_profile_for_id(profileId=userId)
    return (float(profile['profileCompletion']) / 100) * 10


# a user with more matches will be given more score
async def calculate_matching_score(userId):
    return random.uniform(0, 1)

# How active a user is calculated by counting their total swipes
async def calculate_activity_score(userId):
    """
        superlike -- +4
        like -- +2
        dislike -- -1
    """
    user_like_list = await user_liked_profiles(userId=userId)
    user_dislike_list = await user_disliked_profiles(userId=userId)
    user_superlike_list = await user_superliked_profiles(userId=userId)
    return (4 * len(user_superlike_list)) + (2 * len(user_like_list)) + len(user_dislike_list)

    
async def store_profile_grading_firestore(userId=None, userData=None):
    try:
        timestamp = time.time()
        # store for quick access of grades
        await async_db.collection('ProfilesGrading').document(userId).set({"totalScore": userData.total_score, 
                                                                        "id":userId,
                                                                        "popularityScore": userData.popularity_score,
                                                                        "profileCompletionScore": userData.profile_completion_score,
                                                                        "activityScore":userData.activity_score,
                                                                        "matchingScore":userData.matching_score,
                                                                        "userRank":userData.user_rank,
                                                                        "timestamp": timestamp})
        # for historical storage of profile scores
        await async_db.collection('ProfilesGrading').document(userId).collection(userId).document(str(timestamp)).set({
                                                        "totalScore": userData.total_score, 
                                                        "id":userId,
                                                        "popularityScore": userData.popularity_score,
                                                        "profileCompletionScore": userData.profile_completion_score,
                                                        "activityScore":userData.activity_score,
                                                        "matchingScore":userData.matching_score,
                                                        "userRank":userData.user_rank,
                                                        "timestamp": timestamp})
        print(f"Profile grading for {userId} stored successfully.")
    except Exception as e:
        print(f"Exception in storing profile grading for {userId}: {e}")


if __name__ == '__main__':
    asyncio.run(main())