from flask import jsonify, json

# Recommendation system 

'''
    Components of Recommendation System
    1. Recommendation system will be personalized for every user
        a. Filters should be regarded but not followed 
        b. Location
        c. Query from General Principles DB
        d. Curious/Crazy Questions
        e. Likes, Disliked and SuperLikes are part of recommendation system
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

    Cards should contain
        i. A+
        ii. Which match users shallow preference - Filters
        iv. Chance for second user to be liked as well.
        iii. When a user creates a meanigful connection - Question.. e.g. 2022 question

    Matcher Engine * Main - Stream Chat API
    Recommmendation System * Main
    SuperLiked By
    '''


class RecommendationEngine(object):

    def __init__(self):
        pass

    def locationFiltering(self, userLocation=None):
        pass

    def applyFilters(self):
        # filter by 
        # gender
        # religion