from logging import exception
import time
from datetime import datetime
from ProjectConf.FirestoreConf import async_db, db
from ProjectConf.LoggerConf import logger
from Services.UnmatchService import unmatch_test_function


def unmatch_two_profiles(user_id_1, user_id_2):
    unmatch_test_function(user_id_1, user_id_2)

def unreport_profile(reported_profile_id, userId):
    db.collection('ReportedProfile').document(reported_profile_id).collection(userId).document("ReportingDetails").delete()

def match_two_profiles(user_id_1, user_id_2):
    """
    LikesDislikes Match Collection
    RecentChats Collection
    """
    match_ref = db.collection('LikesDislikes').document(user_id_1).collection("Match").document(user_id_2)
    match_ref.delete()
    other_match_ref = db.collection('LikesDislikes').document(user_id_2).collection("Match").document(user_id_1)
    other_match_ref.delete()

    db.collection("LikesDislikes").document(user_id_1).collection("Match").document(user_id_2).set({"id": user_id_2, "timestamp": time.time()})
    db.collection("LikesDislikes").document(user_id_2).collection("Match").document(user_id_1).set({"id": user_id_1, "timestamp": time.time()})
    
    giver_profile = db.collection("Profiles").document(user_id_2).get().to_dict()

    receiver_profile = db.collection("Profiles").document(user_id_1).get().to_dict()

    db.collection("RecentChats").document(user_id_1).collection("Messages").document(user_id_2).set({"fromId": user_id_1, "toId": user_id_2, 
    "timestamp": datetime.now(), "lastText": "", "user": {"firstName": giver_profile["firstName"], "lastName": giver_profile["lastName"], 
    "image1": giver_profile["image1"], "id": user_id_2}, "otherUserUpdated": True})

    db.collection("RecentChats").document(user_id_2).collection("Messages").document(user_id_1).set({"fromId": user_id_2, "toId": user_id_1, 
    "timestamp": datetime.now(), "lastText": "", "user": {"firstName": receiver_profile["firstName"], "lastName": receiver_profile["lastName"], 
    "image1": receiver_profile["image1"], "id": user_id_1}, "otherUserUpdated": True})