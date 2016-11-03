import requests, re, time, json, os
from bs4 import BeautifulSoup

scriptDirectory = os.path.abspath(os.path.dirname(__file__))
userSession = requests.Session()

pendingFileName = 'pendingUsers.txt'
acceptedFileName = 'acceptedUsers.txt'
ignoredFileName = 'ignoredUsers.txt'

pendingFilePath = scriptDirectory + '/' + pendingFileName
acceptedFilePath = scriptDirectory + '/' + acceptedFileName
ignoredFilePath = scriptDirectory + '/' + ignoredFileName

login_params = {
	'utf8': '\u2713',
	'authenticity_token': '',
	'login': input('Whats your username?: '),
	'password': input('Whats your password?: ')
}

generic_headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
}

csrf_headers = {
	'X-CSRF-Token': '',
	'X-Requested-With': 'XMLHttpRequest',
	'User-Agent': generic_headers['User-Agent']
}

pendingFollowList = []
acceptedFollowList = []
ignoredFollowList = []

def retrieveLists():
	global pendingFilePath, acceptedFilePath, ignoredFilePath
	global pendingFollowList, acceptedFollowList, ignoredFollowList
	if os.path.exists(pendingFilePath):
		with open(pendingFilePath, 'r') as f:
			pendingFollowList = json.loads(f.read())
	if os.path.exists(acceptedFilePath):
		with open(acceptedFilePath, 'r') as f:
			acceptedFollowList = json.loads(f.read())
	if os.path.exists(ignoredFilePath):
		with open(ignoredFilePath, 'r') as f:
			ignoredFollowList = json.loads(f.read())

def isUserPending(targetUserName):
	global pendingFollowList
	userPending = False
	for i, v in enumerate(pendingFollowList):
		if v['name'] == targetUserName:
			userPending = True
			break
	return userPending

def isUserAccepted(targetUserName):
	global acceptedFollowList
	userAccepted = False
	for i, v in enumerate(acceptedFollowList):
		if v['name'] == targetUserName:
			userAccepted = True
			break
	return userAccepted

def isUserIgnored(targetUserName):
	global ignoredFollowList
	userIgnored = False
	for i, v in enumerate(ignoredFollowList):
		if v['name'] == targetUserName:
			userIgnored = True
			break
	return userIgnored

def followUser(targetUserName):
	global userSession
	continueLoop = True
	while continueLoop:
		try:
			followResp = userSession.post('https://dribbble.com/' + targetUserName + '/followers', timeout = 5, headers = csrf_headers)
			if followResp.status_code == 201:
				print('Followed ' + targetUserName + '.')
				continueLoop = False
			elif followResp.status_code == 403:
				print('A server error (403) occured. Generally caused by rate-limiting issues. Retrying...')
				print('Error page: ' + followResp.url)
				time.sleep(15)
			elif targetUserInfo.status_code == 404: # Assuming 404 = User doesn't exist / deleted their account.
				continueLoop = False
				print('User \'' + targetUserName + '\' no longer exists, so not following.')
				continue
			else:
				print('A server error (' + str(followResp.status_code) + ') occured. Retrying...')
				print('Error page: ' + followResp.url)
				time.sleep(5)
		except requests.exceptions.RequestException:
			print('Web page timed out. Retrying...')
			time.sleep(5)
	addUserToPendingList(targetUserName)
	time.sleep(1)

def addUserToPendingList(targetUserName):
	global pendingFollowList, pendingFilePath
	pendingFollowList.append({'name': targetUserName, 'time_followed': time.time()})
	with open(pendingFilePath, 'w') as f:
		f.write(json.dumps(pendingFollowList))

def addUserToAcceptedList(targetUserName):
	global acceptedFollowList, acceptedFilePath
	acceptedFollowList.append({'name': targetUserName, 'time_followed': time.time()})
	with open(acceptedFilePath, 'w') as f:
		f.write(json.dumps(acceptedFollowList))

def addUserToIgnoredList(targetUserName):
	global ignoredFollowList, ignoredFilePath
	ignoredFollowList.append({'name': targetUserName, 'time_followed': time.time()})
	with open(ignoredFilePath, 'w') as f:
		f.write(json.dumps(ignoredFollowList))

def unfollowUser(targetUserName):
	global userSession
	continueLoop = True
	while continueLoop:
		try:
			unfollowResp = userSession.delete('https://dribbble.com/' + targetUserName + '/followers/' + targetUserName, timeout = 5, headers = csrf_headers)
			if unfollowResp.status_code == 200:
				print('Unfollowed ' + targetUserName + '.')
				continueLoop = False
			elif unfollowResp.status_code == 403:
				print('A server error (403) occured. Generally caused by rate-limiting issues. Retrying...')
				print('Error page: ' + unfollowResp.url)
				time.sleep(15)
			elif unfollowResp.status_code == 404:
				print('User \'' + targetUserName + '\' no longer exists, so not unfollowing.')
				continueLoop = False
			else:
				print('A server error (' + str(unfollowResp.status_code) + ') occured. Retrying...')
				print('Error page: ' + unfollowResp.url)
				time.sleep(5)
		except requests.exceptions.RequestException:
			print('Web page timed out. Retrying...')
			time.sleep(5)
	time.sleep(1)

def removeUserFromPendingList(targetUserName):
	global pendingFollowList, pendingFilePath
	for i, v in enumerate(list(pendingFollowList)):
		if v['name'] == targetUserName:
			pendingFollowList.remove(v)
			break
	with open(pendingFilePath, 'w') as f:
		f.write(json.dumps(pendingFollowList))

def removeUserFromAcceptedList(targetUserName):
	global acceptedFollowList, acceptedFilePath
	for i, v in enumerate(list(acceptedFollowList)):
		if v['name'] == targetUserName:
			acceptedFollowList.remove(v)
			break
	with open(acceptedFilePath, 'w') as f:
		f.write(json.dumps(acceptedFollowList))

def removeUserFromIgnoredList(targetUserName):
	global ignoredFollowList, ignoredFilePath
	for i, v in enumerate(list(ignoredFollowList)):
		if v['name'] == targetUserName:
			ignoredFollowList.remove(v)
			break
	with open(ignoredFilePath, 'w') as f:
		f.write(json.dumps(ignoredFollowList))

# Retrieving the list of currently pending followed users by the bot.

retrieveLists()

# Time to remove anyone in any list for more than a week.

currentTime = time.time()
for i, v in enumerate(list(acceptedFollowList)):
	if currentTime - v['time_followed'] > 604800:
		acceptedFollowList.remove(v)
		with open(acceptedFilePath, 'w') as f:
			f.write(json.dumps(acceptedFollowList))

for i, v in enumerate(list(ignoredFollowList)):
	if currentTime - v['time_followed'] > 604800:
		ignoredFollowList.remove(v)
		with open(ignoredFilePath, 'w') as f:
			f.write(json.dumps(ignoredFollowList))

# This is used in order to obtain the authenticity token required for logging in.

continueLoop = True
while continueLoop:
	try:
		loginPage = userSession.get('https://dribbble.com/session/new', timeout = 5, headers = generic_headers)
		if loginPage.status_code == 200:
			continueLoop = False
		elif loginPage.status_code == 403:
			print('A server error (403) occured. Generally caused by rate-limiting issues. Retrying...')
			print('Error page: ' + loginPage.url)
			time.sleep(15)
		else:
			print('A server error (' + str(loginPage.status_code) + ') occured. Retrying...')
			print('Error page: ' + loginPage.url)
			time.sleep(5)
	except requests.exceptions.RequestException:
		print('Web page timed out. Retrying...')
		time.sleep(5)
loginPage_soup = BeautifulSoup(loginPage.text, 'html.parser')
login_params['authenticity_token'] = loginPage_soup.find('input', {'name': 'authenticity_token'}).get('value')

# This is the actual login request.

continueLoop = True
while continueLoop:
	try:
		userLogin = userSession.post('https://dribbble.com/session', data = login_params, timeout = 5, headers = generic_headers)
		if userLogin.status_code == 200:
			continueLoop = False
		elif userLogin.status_code == 403:
			print('A server error (403) occured. Generally caused by rate-limiting issues. Retrying...')
			print('Error page: ' + userLogin.url)
			time.sleep(15)
		else:
			print('A server error (' + str(userLogin.status_code) + ') occured. Retrying...')
			print('Error page: ' + userLogin.url)
			time.sleep(5)
	except requests.exceptions.RequestException:
			print('Web page timed out. Retrying...')
			time.sleep(5)

userLogin_soup = BeautifulSoup(userLogin.text, 'html.parser')
csrf_headers['X-CSRF-Token'] = userLogin_soup.find('meta', {'name': 'csrf-token'}).get('content')

# Time to see who has actually bothered following us.

for i, v in enumerate(list(pendingFollowList)):
	currentTime = time.time()
	if currentTime - v['time_followed'] > 172800: # If it has been more than 24 hours since you followed them...
		continueLoop = True
		while continueLoop:
			try:
				targetUserInfo = userSession.get('https://dribbble.com/' + v['name'] + '/hover_card', timeout = 5)
				if targetUserInfo.status_code == 200:
					continueLoop = False
				elif targetUserInfo.status_code == 403:
					print('A server error (403) occured. Generally caused by rate-limiting issues. Retrying...')
					print('Error page: ' + targetUserInfo.url)
					time.sleep(15)
				elif targetUserInfo.status_code == 404: # Assuming 404 = User doesn't exist / deleted their account.
					continueLoop = False
					print('User \'' + v['name'] + '\' no longer exists, so removing from pending list.')
					removeUserFromPendingList(v['name'])
					continue
				else:
					print('A server error (' + str(targetUserInfo.status_code) + ') occured. Retrying...')
					print('Error page: ' + targetUserInfo.url)
					time.sleep(5)
			except requests.exceptions.RequestException:
				print('Web page timed out. Retrying...')
				time.sleep(5)
		targetUserInfo_soup = BeautifulSoup(targetUserInfo.text, 'html.parser')
		isTargetUserFollowingYou = targetUserInfo_soup.find('a', {'class': 'follow', 'rel': 'tipsy', 'title': 'Follows you'})
		removeUserFromPendingList(v['name'])
		if isTargetUserFollowingYou:
			addUserToAcceptedList(v['name'])
			print(v['name'] + ' followed you. Accepted.')
		else: 
			unfollowUser(v['name'])
			addUserToIgnoredList(v['name'])
			print(v['name'] + ' didn\'t follow you. Ignored and unfollowed.')
		time.sleep(1)
print('Review of followed users finished.')

# Time to view the debuts and follow more people :)

pageNum = 1
continueLoop = True

while continueLoop:
	try:
		debutsPage = userSession.get('https://dribbble.com/shots?list=debuts&page=' + str(pageNum) + '&per_page=12', timeout = 5, headers = generic_headers)
		if debutsPage.status_code == 404: # 404 means we've reached the end of the list.
			continueLoop = False
			continue
		elif debutsPage.status_code == 403:# Likely server rate limiting caused this. 403 if I don't have enough wait timers.
			print('A server error (403) occured. Generally caused by rate-limiting issues. Retrying...')
			print('Error page: ' + debutsPage.url)
			time.sleep(15)
			continue
		elif debutsPage.status_code != 200:
			print('A server error (' + str(debutsPage.status_code) + ') occured. Retrying...')
			print('Error page: ' + debutsPage.url)
			time.sleep(5)
			continue			
	except requests.exceptions.RequestException:
			print('Web page timed out. Retrying...')
			print('Error page: ' + debutsPage.url)
			time.sleep(5)
			continue
	debutsPage_soup = BeautifulSoup(debutsPage.text, 'html.parser')
	debutsCards = debutsPage_soup.find_all('li', {'id': re.compile('^screenshot-\d+$')}) # May change this variable name in the future.
	for debutCard in debutsCards:
		debutUserAttrs = debutCard.find('span', {'class': 'attribution-user'})
		debutUserURL = debutUserAttrs.select('.url.hoverable')[0].get('href')
		debutUserName = debutUserURL[1:]
		if not isUserPending(debutUserName) and not isUserAccepted(debutUserName) and not isUserIgnored(debutUserName):
			followUser(debutUserName)
		else:
			continueLoop = False
			break
	pageNum += 1
print('Finished. No more users left to follow.')
