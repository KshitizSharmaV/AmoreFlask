"""
How will u grade them :
- Grading by popularity. KPI LIkes, SuperLikes and Dislikes
- Profile Completeion 
- How the active user is 
- How responsive user is on messages 
- How many times a person have been reported
        - Nature of Offence
"""
from fetchprofiles import FetchProfiles
import asyncio

class ProfileGradingEngine:
	total_score: float # 0 to 10
	popularity_score: float # 0 to 10
	profile_completion_score: float # 0 to 10
	user_activity_score: float # 0 to 10
	user_responsiveness_score: float # 0 to 10
	user_offence_score: float # will be in negative, 0 to -40

	def __init__(self):
		self.fetch_profiles_object = FetchProfiles()
		self.popularity_score = 0
		self.profile_completion_score = 0
		self.user_activity_score = 0
		self.user_responsiveness_score = 0
		self.user_offence_score = 0

	def calculate_total_score(self, userId):
		self.calculate_popularity_score(userId=userId)
		self.get_profile_completion_score(userId=userId)
		# self.total_score = sum([self.profile_completion_score, self.user_activity_score, self.user_responsiveness_score, self.user_offence_score])/3
		# self.total_score += self.popularity_score
		self.total_score = self.popularity_score + self.profile_completion_score

	def calculate_popularity_score(self, userId):
		"""
			superlike -- +4
			like -- +2
			dislike -- -1
			_______________
			561
			How to convert 561 to a score on 0-10 scale?
		"""
		liked_by_list = self.fetch_profiles_object.profiles_which_liked_user(userId=userId)
		disliked_by_list = self.fetch_profiles_object.profiles_which_disliked_user(userId=userId)
		superliked_by_list = self.fetch_profiles_object.profiles_which_superliked_user(userId=userId)
		self.popularity_score = ((4*len(superliked_by_list)) + (2*len(liked_by_list)) - len(disliked_by_list))

	def get_profile_completion_score(self, userId):
		profile = self.fetch_profiles_object.getProfileForId(profileId=userId)
		self.profile_completion_score = (float(profile['profileCompletion'])/100)*10


if __name__=='__main__':
	profile_grading_engine = ProfileGradingEngine()
	for id in ['06TgfRGj5ssVFQBR', '0RNSh7XU6uxKkX95', '1KNmLbYCKBtGGeRb', '2O7Sxjk2K8Z9Zbir', '2Pnzu3gOeCMm4XqG', '4V2CAn67SvEOXq7W', '5z1WWM9GyoJPMwzK', '6M6mnXyTDWocyjOy', '7M0sJiKQi57WNlPd', '7MXV1mY9i3f1WQzE11ZdG7EvATx1', '7ZSF4qu83lBeX8Mf', '8OQ8W2v6nOT4y3kqYqvVXFpQOaT2', '9TOfKVTRJw2GXL0E', 'A7or1pGHqPB87d1g', 'BD00IjRpBbIesc96', 'CVWpmQBh40FnZpdf', 'EpFs6znr8rV3P45o', 'G42AgiBH62PCzzIv', 'GWkEwboOmHevXHfdhIyiWCAfDE22', 'HsguOfulSC1rmRza', 'JE8ejjw6V5ZKWyc0', 'JcBQeIY2lv3aP2c2', 'Jfzz4niuLuR00Ty8Hhhy9qg7sp03', 'LFAAW0t42BcmbKVC', 'Mhmx4VaaaU6CSJjc', 'O7U1VF2QsZmMTG2k', 'OExxnIeegddEjCTi', 'Qe2hI1HfesfGvVIr', 'QlGDU3do5BS6YZSkeJUN0Npls7D3', 'QvV4OoZmZ3QWHhMNaZrr7lkqmLF3', 'R9HzkBlt9qdmWOIeDOuPnTT7tWi1', 'RrwcrMpbiKUz5djt5I1XBQf643J2', 'VWZ57xjn7ZfvxPdg', 'WDG6Cfh5aNuxWVGc', 'WbZZuRPhxRf6KL1GFHcNWL2Ydzk1', 'X1HPpb0RT5Y9hh6C', 'X3KkZqZQo6NJGupn', 'XOurlov0DxZSp561zDqIfv3pqlt1', 'XmO1QXLV10BnnO8S', 'YFVdbEfVCLGaW6SL', 'YbTlos4mEX6mRo0A', 'YovGQexpE9oXMCtC', 'ZZCKYcm2tW8dG8LG', 'ZgwTr7S2oPaKpALV', 'a6yJBDhqjfr2vvF2', 'a79GFq2F1yATOWu2', 'aF6BqbMvkHiXt52N', 'eVsTeXVjOFbDc48x', 'fGjPbsQq62IDvHVG', 'fv2RC90px78DuIrN', 'fvLGMuWzzbFnO7KV', 'hwFIcicYwPXYsL88n55fll7JuEM2', 'jaOQPePYT510dyin', 'k692VKviEbXULblA', 'lNJkCUfWiUtBGjMs', 'nOVgZ08Co4NS5p96', 'nhoXRc3wBSbU9YF9pMbSRDmIh8h2', 'p7Gws6QkWxz0v4lm', 'penesHeuqWtQu5ZA', 'sCZ7nWrH1uR4QfAGj6Ndz4Cp3Vv2', 'wClaPCcm3Qblg5YBYO7qQdOdJdn2', 'xUNQA8a6ShBk8vg7', 'y39LCk1SCOw2gBiG', 'yCvln20Ent2yvYf5', 'zI9DqdXcrEenpKk8QjccnNVY4KA3', 'zopU4FMeBKzzQx7z']:
		profile_grading_engine.calculate_total_score(userId=id)
		print(f"profile popularity score for {id}: {profile_grading_engine.popularity_score}")
		print(f"profile profile completion score for {id}: {profile_grading_engine.profile_completion_score}")
		print(f"profile grading score for {id}: {profile_grading_engine.total_score}")
		print("__________________________________________________________________________________________")