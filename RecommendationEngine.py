from flask import jsonify, json
from fetchprofiles import FetchProfiles

# Recommendation system 

"""
    Components of Recommendation System
    1. Recommendation system will be personalized for every user
        a. Filters should be regarded but not followed 
            - Career Preference
            - Community Preference
            - Country Preference
            - Education Preference
            - Gender Preference
            - Religion Preference
        b. Location
            - Distance of profile from User
        c. Interests
        d. Sexual Orientation (if visible)
        e. Query from General Principles DB
        f. Curious/Crazy Questions
        g. Likes, Disliked and SuperLikes are part of recommendation system

    2. General Principles it should work on?
        a. Profile with high score and more complete profiles will be priortized over profiles with no data
        b. This will have a score and a collection where profiles are listed by scores

    Analysis - Scoring?
        a. the profiles we show have to be good - they are A+
            i. SuperLikes - KPI, the profile which is like a star profile
            ii. 
        b. You want it to be tailored to a person's personality 
            i. You can do that by asking right question? 
    
    Grading
        i. A+ 5%
        ii. B 10%
        iii C 35%
        iv. D 30%
        v E 20%

    How will u grade them :
        i. Grading by popularity. KPI LIkes, SuperLikes and Dislikes
        ii. Profile Completeion 
        iii. How the active user is 
        iv. How responsive user is on messages 
        v. How many times a person have been reported
            - Nature of Offence

    Cards should contain
        i. A+
        ii. Which match users shallow preference - Filters
        iv. Chance for second user to be liked as well.
        iii. When a user creates a meanigful connection - Question.. e.g. 2022 question

    Matcher Engine * Main - Stream Chat API
    Recommmendation System * Main
    SuperLiked By
"""

class RecommendationEngine(object):
    filter_and_location_data: dict
    user_profile_data: dict
    profiles_array: list
    career_pref: list
    community_pref: list
    country_pref: str
    education_pref: str
    gender_pref: str
    religion_pref: list
    user_interests: list
    users_show_me_pref: str


    def __init__(self, db, logger):
        self.db = db
        self.logger = logger

    def fetch_filter_and_location_data(self, userId):
        col_ref = self.db.collection('FilterAndLocation')
        doc_ref = col_ref.document(userId)
        doc = doc_ref.get()
        self.filter_and_location_data = doc.to_dict()

    def fetch_user_profile_data(self, userId):
        col_ref = self.db.collection('Profiles')
        doc_ref = col_ref.document(userId)
        doc = doc_ref.get()
        self.user_profile_data = doc.to_dict()

    def get_preferences(self, userId):
        self.profiles_array = FetchProfiles(db=self.db, logger=self.logger).getProfiles(userId=userId)
        self.career_pref = self.filter_and_location_data['careerPreference']
        self.community_pref = self.filter_and_location_data['communityPreference']
        self.country_pref = self.filter_and_location_data['countryPreference']
        self.education_pref = self.filter_and_location_data['educationPreference']
        self.gender_pref = self.filter_and_location_data['genderPreference']
        self.religion_pref = self.filter_and_location_data['religionPreference']
        self.user_interests = self.user_profile_data['interests']
        self.users_show_me_pref = self.user_profile_data['showMePreference']

    def location_filtering(self, distancePreference=None):
        pass

    def country_filter(self, profile):
        if "country" in profile.keys():
            if profile['country'] == self.country_pref:
                return True
            else:
                return False
        else:
            return False

    def religion_filter(self, profile):
        if "religion" in profile.keys():
            if profile['religion'] == self.religion_pref:
                return True
            else:
                return False
        else:
            return False

    def applyFilters(self, userId):
        """
        Strict Filtering by: 
        - Country
        - Show Me Preference -- Gender
        - Religion
        - Distance of Profile from User
        """
        self.fetch_filter_and_location_data(userId=userId)
        self.fetch_user_profile_data(userId=userId)
        self.get_preferences(userId=userId)
        filtered = list(filter(self.country_filter, self.profiles_array))
        filtered = list(filter(lambda x: x['genderIdentity'] == self.users_show_me_pref, filtered))
        filtered = list(filter(self.religion_filter, filtered))
        return filtered