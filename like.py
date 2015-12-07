#!/usr/bin/python
#
# automatically like photos by hashtag, location or popularity
#
import requests, json, pprint, cookielib, time, random, yaml, sys, logging, os
from requests import request, session
from collections import Counter

# logging
FORMAT = '%(asctime)s %(message)s' 
LOG_FILENAME = os.path.dirname(os.path.abspath(__file__)) + '/log.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format=FORMAT)

WEBSTA_URL = "http://websta.me/api/like/"
headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 
'Accept-Encoding': 'gzip, deflate', 
'Accept-Language': 'en-US,en;q=0.5', 
#'Cookie': '	__cfduid=ddd7e7fe8e28e6f38a8577bac9940c0101434928747; is_message_first_access=1; is_first_access=1; _lb.u=1%2Fcf9431de6974c6dfd3fd82c3c8eb22ab%3A; PHPSESSID=nc3li4t174negni9mmg7k0l732', 
'Host': 'websta.me', 
'Referer': 'http://websta.me/', 
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0', 
'X-Requested-With': 'XMLHttpRequest'
}


cj = cookielib.MozillaCookieJar('pycookie.txt')
cj.load()
#print str(cj)

# Function to read the hashtags from file
def getHashtagsFromFile():
	hashtags = []
	filename = os.path.dirname(os.path.abspath(__file__)) + '/hashtags.txt'
	f = open(filename)
	hashtags = [line.strip().decode("ascii","ignore").encode("ascii") for line in open(filename)]
	f.close()
	hashtag = random.choice(hashtags)
	return hashtag

# Like photos based on a given locations
def likeLocation():
	GOOGLE_API_KEY = str(profile['CREDENTIALS']['GOOGLE_API_KEY'])
	CITY = str(profile['LOCATION']['CITY'])
	STATE = str(profile['LOCATION']['STATE'])
	COUNTRY = str(profile['LOCATION']['COUNTRY'])
	GOOGLE_LOCATION = "https://maps.googleapis.com/maps/api/geocode/json?address=" + CITY + ",+" + STATE + ",+" + COUNTRY + "&key=" + GOOGLE_API_KEY

	lat_long = requests.get(GOOGLE_LOCATION).json()
	lat = lat_long['results'][0]['geometry']['location']['lat']
	lng = lat_long['results'][0]['geometry']['location']['lng']
	CLIENT_ID = str(profile['CREDENTIALS']['INSTAGRAM_CLIENT_ID'])
	IG_GEO = "https://api.instagram.com/v1/media/search?lat=" + str(lat) + "&lng=" + str(lng) + "&client_id=" + CLIENT_ID
	likes = 0
	print "Liking posts in " + CITY + " " + STATE + " " + COUNTRY
	logging.debug("Liking posts in " + CITY + " " + STATE + " " + COUNTRY)
	while True:
		scrape_ids = requests.get(IG_GEO).json()
		for i in range(0, 20):
			id = scrape_ids['data'][i]['id']
			LIKE = WEBSTA_URL + id
			r = requests.get(LIKE, headers=headers, cookies=cj)
			if "200" in str(r.status_code):
				if '"status":"OK","message":"LIKED"' in r.text:
					likes += 1
					print "YOU LIKED http://websta.me/p/" + str(id) + " " + str(r.text) + " total likes: " + str(likes)
					logging.debug("YOU LIKED http://websta.me/p/" + str(id) + " " + str(r.text) + " total likes: " + str(likes))
				else:
					print "http://websta.me/p/" + str(id) + " PHOTO LIKED PREVIOUSLY OR SKIPPED"
					logging.debug("http://websta.me/p/" + str(id) + " PHOTO LIKED PREVIOUSLY OR SKIPPED")
			else:
				print "THERE WAS AN ERROR WITH THE RESPONSE.  STATUS CODE: " + str(r.status_code)
				logging.debug("THERE WAS AN ERROR.  STATUS CODE: " + str(r.status_code))
				sys.exit()	
				break
			if likes >= random.randint(int(min_like), int(max_like)):
				print "MAX LIKES REACHED: " + str(likes)
				logging.debug("MAX LIKES REACHED: " + str(likes))
				sys.exit()
				break
			time.sleep(random.randint(int(min_sleep_like), int(max_sleep_like)))
		IG_GEO = "https://api.instagram.com/v1/media/search?lat=" + str(lat) + "&lng=" + str(lng) + "&client_id=" + CLIENT_ID + "&max_id=" + str(id)
	print "Done"
	logging.debug("Done")

# Like the most popular photos on instagram
def likePopular():
	CLIENT_ID = str(profile['CREDENTIALS']['INSTAGRAM_CLIENT_ID'])
	IG_POPULAR_URL = "https://api.instagram.com/v1/media/popular?client_id=" + CLIENT_ID
	likes = 0
	print "Liking popular posts..."
	logging.debug("Liking popular posts...")
	while True:
		scrape_ids = requests.get(IG_POPULAR_URL).json()
		for i in range(0, 20):
			id = scrape_ids['data'][i]['id']
			LIKE = WEBSTA_URL + id
			r = requests.get(LIKE, headers=headers, cookies=cj)
			if "200" in str(r.status_code):
				if '"status":"OK","message":"LIKED"' in r.text:
					likes += 1
					print "YOU LIKED http://websta.me/p/" + str(id) + " " + str(r.text) + " total likes: " + str(likes)
					logging.debug("YOU LIKED http://websta.me/p/" + str(id) + " " + str(r.text) + " total likes: " + str(likes))
				else:
					print "http://websta.me/p/" + str(id) + " PHOTO LIKED PREVIOUSLY OR SKIPPED"
					logging.debug("http://websta.me/p/" + str(id) + " PHOTO LIKED PREVIOUSLY OR SKIPPED")
			else:
				print "THERE WAS AN ERROR WITH THE RESPONSE.  STATUS CODE: " + str(r.status_code)
				logging.debug("THERE WAS AN ERROR.  STATUS CODE: " + str(r.status_code))
				sys.exit()	
				break
			if likes >= random.randint(int(min_like), int(max_like)):
				print "MAX LIKES REACHED: " + str(likes)
				logging.debug("MAX LIKES REACHED: " + str(likes))
				sys.exit()
				break
			time.sleep(random.randint(int(min_sleep_like), int(max_sleep_like)))
		IG_POPULAR_URL = "https://api.instagram.com/v1/media/popular?client_id=" + CLIENT_ID + "&max_id=" + str(id)
	print "Done"
	logging.debug("Done")

# Like most recent photos based on hashtag
def likeHashtag():
	hashtags = []
	filename = os.path.dirname(os.path.abspath(__file__)) + '/hashtags.txt'
	f = open(filename)
	hashtags = [line.strip().decode("ascii","ignore").encode("ascii") for line in open(filename)]
	f.close()
	hashtag = random.choice(hashtags)

	CLIENT_ID = str(profile['CREDENTIALS']['INSTAGRAM_CLIENT_ID'])
	IG_TAG_URL = "https://api.instagram.com/v1/tags/" + hashtag + "/media/recent?client_id=" + CLIENT_ID
	likes = 0
	print "Liking posts tagged #" + hashtag
	logging.debug("Liking posts tagged #" + hashtag)
	while True:
		scrape_ids = requests.get(IG_TAG_URL).json()
		for i in range(0, 20):
			id = scrape_ids['data'][i]['id']
			LIKE = WEBSTA_URL + id
			r = requests.get(LIKE, headers=headers, cookies=cj)
			if "200" in str(r.status_code):
				if '"status":"OK","message":"LIKED"' in r.text:
					likes += 1
					print "YOU LIKED http://websta.me/p/" + str(id) + " " + str(r.text) + " total likes: " + str(likes)
					logging.debug("YOU LIKED http://websta.me/p/" + str(id) + " " + str(r.text) + " total likes: " + str(likes))
				else:
					print "http://websta.me/p/" + str(id) + " PHOTO LIKED PREVIOUSLY OR SKIPPED"
					logging.debug("http://websta.me/p/" + str(id) + " PHOTO LIKED PREVIOUSLY OR SKIPPED")
			else:
				print "THERE WAS AN ERROR WITH THE RESPONSE.  STATUS CODE: " + str(r.status_code)
				logging.debug("THERE WAS AN ERROR.  STATUS CODE: " + str(r.status_code))
				sys.exit()	
				break
			if likes >= random.randint(int(min_like), int(max_like)):
				print "MAX LIKES REACHED: " + str(likes)
				logging.debug("MAX LIKES REACHED: " + str(likes))
				sys.exit()
				break
			time.sleep(random.randint(int(min_sleep_like), int(max_sleep_like)))
		IG_TAG_URL = "https://api.instagram.com/v1/tags/" + str(hashtag) + "/media/recent?client_id=" + CLIENT_ID + "&max_id=" + str(id)
	print "Done"
	logging.debug("Done")

# Like most recent photos based on hashtag
def test():
	hashtags = []
	filename = os.path.dirname(os.path.abspath(__file__)) + '/hashtags.txt'
	f = open(filename)
	hashtags = [line.strip().decode("ascii","ignore").encode("ascii") for line in open(filename)]
	f.close()
	hashtag = random.choice(hashtags)

	CLIENT_ID = str(profile['CREDENTIALS']['INSTAGRAM_CLIENT_ID'])
	IG_TAG_URL = "https://api.instagram.com/v1/tags/" + hashtag + "/media/recent?client_id=" + CLIENT_ID
	likes = 0
	count = 0
	print "Liking posts tagged #" + hashtag
	logging.debug("Liking posts tagged #" + hashtag)
	while True:
		scrape_ids = requests.get(IG_TAG_URL).json()
		lorem = scrape_ids['data'][i]['id']
		c = Counter(lorem) 
		print c
		#print len(str(id))
		for ids in scrape_ids['data']:
			
			print ids['id']
			count += 1
			time.sleep(1)
		print str(count)
		sys.exit()

		#for ids in scrape_ids['data']:
		#for i in range(0, 20):
			#id = scrape_ids['data'][i]['id']
			#LIKE = WEBSTA_URL + id
			#r = requests.get(LIKE, headers=headers, cookies=cj)
			#if "200" in str(r.status_code):
			#	if '"status":"OK","message":"LIKED"' in r.text:
			#		likes += 1
			#		print "YOU LIKED http://websta.me/p/" + str(id) + " " + str(r.text) + " total likes: " + str(likes)
			#		logging.debug("YOU LIKED http://websta.me/p/" + str(id) + " " + str(r.text) + " total likes: " + str(likes))
			#	else:
			#		print "http://websta.me/p/" + str(id) + " PHOTO LIKED PREVIOUSLY OR SKIPPED"
			#		logging.debug("http://websta.me/p/" + str(id) + " PHOTO LIKED PREVIOUSLY OR SKIPPED")
			#else:
			#	print "THERE WAS AN ERROR WITH THE RESPONSE.  STATUS CODE: " + str(r.status_code)
			#	logging.debug("THERE WAS AN ERROR.  STATUS CODE: " + str(r.status_code))
			#	sys.exit()	
			#	break
			#if likes >= random.randint(int(min_like), int(max_like)):
			#	print "MAX LIKES REACHED: " + str(likes)
			#	logging.debug("MAX LIKES REACHED: " + str(likes))
			#	sys.exit()
			#	break
			#time.sleep(random.randint(int(min_sleep_like), int(max_sleep_like)))
		#IG_TAG_URL = "https://api.instagram.com/v1/tags/" + str(hashtag) + "/media/recent?client_id=" + CLIENT_ID + "&max_id=" + str(id)
	print "Done"
	logging.debug("Done")

if __name__ == "__main__":

	profile = yaml.safe_load(open(os.path.dirname(os.path.abspath(__file__)) + "/profile.yml", "r"))
	min_like = profile['LIKES']['MIN']
	max_like = profile['LIKES']['MAX']
	min_sleep_like = profile['SLEEP_PER_LIKE']['MIN']
	max_sleep_like = profile['SLEEP_PER_LIKE']['MAX']
	min_sleep_start = profile['SLEEP_START']['MIN']
	max_sleep_start = profile['SLEEP_START']['MAX']

	print "sleep start..."
	logging.debug("sleep start")
	time.sleep(random.randint(int(min_sleep_start), int(max_sleep_start)))

	if profile['MODE']['LIKE_POPULAR'] == "TRUE":
		likePopular()
	else:
		pass

	if profile['MODE']['LIKE_HASHTAGS'] == "TRUE":
		#hashtag = getHashtagsFromFile()
		#likeHashtag(hashtag)
		likeHashtag()
	else:
		pass

	if profile['MODE']['LIKE_LOCATION'] == "TRUE":
		likeLocation()
	else:
		pass

	if profile['MODE']['TEST'] == "TRUE":
		test()
	else:
		pass

	sys.exit()