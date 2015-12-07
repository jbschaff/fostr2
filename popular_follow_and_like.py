#!/usr/bin/python

import requests, json, pprint, cookielib, time, random, yaml, sys, logging, os
from requests import request, session

# logging
FORMAT = '%(asctime)s %(message)s' 
LOG_FILENAME = os.path.dirname(os.path.abspath(__file__)) + '/log.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format=FORMAT)

WEBSTA_FOLLOW_URL = "http://websta.me/api/relationships/"
follow_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 
'Accept-Encoding': 'gzip, deflate', 
'Accept-Language': 'en-US,en;q=0.5', 
'Host': 'websta.me', 
'Content-Type':	'application/x-www-form-urlencoded; charset=UTF-8',
'Referer': 'http://websta.me/', 
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0', 
'X-Requested-With': 'XMLHttpRequest',
}

payload = {'action': 'follow'}

WEBSTA_LIKE_URL = "http://websta.me/api/like/"
like_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 
'Accept-Encoding': 'gzip, deflate', 
'Accept-Language': 'en-US,en;q=0.5', 
'Host': 'websta.me', 
'Referer': 'http://websta.me/', 
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0', 
'X-Requested-With': 'XMLHttpRequest'
}

cj = cookielib.MozillaCookieJar('pycookie.txt')
cj.load()

# Like the most popular photos on instagram
def followandlike():
	CLIENT_ID = str(profile['CREDENTIALS']['INSTAGRAM_CLIENT_ID'])

	#for i in range (0,19):
	#get most recent popular posts
	#IG_POPULAR_URL = "https://api.instagram.com/v1/media/popular?client_id=" + CLIENT_ID

	#for i in range (0,19):
	#get the ids of the people who have liked the photo
	#FOLLOWERS_URL = "https://api.instagram.com/v1/media/" + photo_id + "/likes?client_id=" + CLIENT_ID

	#for i in rage (0,19):
	#get a users most recent posts
	#USER_MEDIA = "https://api.instagram.com/v1/users/" + user_id + "/media/recent/?client_id=" + CLIENT_ID

	total_likes = 0
	
	user_follow = 0

	print "Picking a user"
	users = []
	filename = os.path.dirname(os.path.abspath(__file__)) + '/users.txt'
	f = open(filename)
	users = [line.strip().decode("ascii","ignore").encode("ascii") for line in open(filename)]
	f.close()
	user_id = random.choice(users)

	while True:

		#get recent post in json format
		print "Get all recent posts for user " + user_id
		IG_POPULAR_URL = "https://api.instagram.com/v1/media/popular?client_id=" + CLIENT_ID
		scrape_ids = requests.get(IG_POPULAR_URL).json()
		for i in range(0, 19):

			#get the ids of the popular photos
			print "Picking an single post..."
			photo_id = scrape_ids['data'][i]['id']
			print "Picked post: http://websta.me/p/" + photo_id
			
			#get the ids of the people who have liked the e
			print "Getting ids of users who liked photo..."
			FOLLOWERS_URL = "https://api.instagram.com/v1/media/" + photo_id + "/likes?client_id=" + CLIENT_ID
			scrape_users = requests.get(FOLLOWERS_URL).json()
			for i in range(0, 19):

				print "Picking one of the users who liked the photo..."
				user_id = scrape_users['data'][i]['id']

				#follow a user
				print "Following one of the users..." + user_id
				FOLLOW = WEBSTA_FOLLOW_URL + user_id
				r = requests.post(FOLLOW, headers=follow_headers, cookies=cj, data=payload)
				user_follow += 1
				print str(r.text)
				if user_follow >= random.randint(int(min_follow), int(max_follow)):
					print "You followed enough people"
					logging.debug("You followed enough people")
					sys.exit()
					break
				time.sleep(random.randint(int(min_sleep_like), int(max_sleep_like)))

				if '"target_user_is_private":true' in r.text:
					pass
				else: 
					#get the followers most recent photos
					print "Getting the user's mot recent photos..."
					USER_MEDIA = "https://api.instagram.com/v1/users/" + user_id + "/media/recent/?client_id=" + CLIENT_ID
					scrape_photos = requests.get(USER_MEDIA).json()

					user_likes = 0

					#ids = scrape_users['data'][i]['id']

					#for id in ids.iteritems():
					for ids in scrape_photos['data']:
					
					#for i in range(0, 19):
						try: 
							user_photo_id = scrape_photos['data'][i]['id']
						except IndexError:
							print "not enough photos...moving on"
							break
						else:

							#like their most recent photo
							print "Like one of the user's most recent photos..."
							LIKE = WEBSTA_LIKE_URL + user_photo_id
							r = requests.get(LIKE, headers=like_headers, cookies=cj)
							if "200" in str(r.status_code):
								if '"status":"OK","message":"LIKED"' in r.text:
									user_likes += 1
									total_likes += 1
									print "YOU LIKED http://websta.me/p/" + str(user_photo_id) + " " + str(r.text) + " user likes: " + str(user_likes) + " total likes: " + str(total_likes)
									logging.debug("YOU LIKED http://websta.me/p/" + str(user_photo_id) + " " + str(r.text) + " user likes: " + str(user_likes) + " total likes: " + str(total_likes))
								else:
									print "http://websta.me/p/" + str(user_photo_id) + " PHOTO LIKED PREVIOUSLY OR SKIPPED"
									logging.debug("http://websta.me/p/" + str(user_photo_id) + " PHOTO LIKED PREVIOUSLY OR SKIPPED")
							else:
								print "THERE WAS AN ERROR WITH THE RESPONSE.  STATUS CODE: " + str(r.status_code)
								logging.debug("THERE WAS AN ERROR.  STATUS CODE: " + str(r.status_code))
								sys.exit()	
								break
							if user_likes >= random.randint(int(per_user_min_like), int(per_user_max_like)):
								print "MAX LIKES REACHED FOR THIS USER: " + str(user_likes)
								logging.debug("MAX LIKES REACHED: " + str(user_likes))
								break
							if total_likes >= random.randint(int(total_min_like), int(total_max_like)):
								print "TOTAL MAX LIKES REACHED: " + str(total_likes)
								logging.debug("MAX LIKES REACHED: " + str(total_likes))
								sys.exit()
								break
							time.sleep(random.randint(int(min_sleep_follow), int(max_sleep_follow)))

if __name__ == "__main__":

	profile = yaml.safe_load(open(os.path.dirname(os.path.abspath(__file__)) + "/profile_follow.yml", "r"))
	total_min_like = profile['LIKES']['TOTAL_MIN']
	total_max_like = profile['LIKES']['TOTAL_MAX']
	per_user_min_like = profile['LIKES']['PER_USER_MIN']
	per_user_max_like = profile['LIKES']['PER_USER_MAX']

	min_follow = profile['FOLLOW']['MIN']
	max_follow = profile['FOLLOW']['MAX']

	min_sleep_start = profile['SLEEP_START']['MIN']
	max_sleep_start = profile['SLEEP_START']['MAX']

	min_sleep_like = profile['SLEEP_PER_LIKE']['MIN']
	max_sleep_like = profile['SLEEP_PER_LIKE']['MAX']

	min_sleep_follow = profile['SLEEP_PER_FOLLOW']['MIN']
	max_sleep_follow = profile['SLEEP_PER_FOLLOW']['MAX']

	print "sleep start..."
	logging.debug("sleep start")
	time.sleep(random.randint(int(min_sleep_start), int(max_sleep_start)))

	followandlike()

	sys.exit()