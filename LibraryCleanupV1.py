import Image
import imghdr
import os
from pyplex.server import Server
import time
import sys
import hashlib
import re

CacheDirectory = "/home/petej/Plex/Library/Application Support/Plex Media Server/Cache/PhotoTranscoder"
SearchDirectory = "/home/petej/Plex/Library/Application Support/Plex Media Server/Metadata"

PeriodicMessageTime = 10

MovieKeys = []
MovieHashes = []

ShowKeys = []
ShowHashes = []

server = Server("diskstation", 32400)
print server

server.libraryRefresh()
for x in range(0, 6):
	print x
	time.sleep(10)

start_time = time.time()
print_time = time.time()
filecount = 0
for section in server.library.sections:
	if not "Unsorted" in str(section):
		section.emptyTrash()
		time.sleep(5)
		start_time = time.time()
		content = section.getContent('all')
		print section, len(content),  " ", time.time() - start_time, "seconds"
		for show in content:
			if time.time() - print_time >= PeriodicMessageTime:
				print filecount, time.time() - start_time, show
				print_time = time.time()
			filecount += 1
			guid = show.getGuid()
			if guid is None or "none" in guid:
				print "Rematching: ", show
				show.match()

print "Cleaning"
server.cleanBundles()
time.sleep(5)
print "Optimizing"
server.optimize()
time.sleep(5)

i = 0
for section in server.library.movies:
	if not "Unsorted" in str(section):
		start_time = time.time()
		content = section.getContent('all')
		print section, len(content), " ", time.time() - start_time, "seconds"
		for movie in content:
			start_time = time.time()
			guid = movie.getGuid()
			m = hashlib.sha1()
			m.update(guid) 
			key = m.hexdigest()
			MovieKeys.append(str(movie.key))
			MovieHashes.append(str(key))
			print i, key, movie, " ", time.time() - start_time, "seconds"
			i = i + 1

for section in server.library.shows:
	if not "Unsorted" in str(section):
		start_time = time.time()
		content = section.getContent('all')
		print section, len(content), " ", time.time() - start_time, "seconds"
		for show in content:
			start_time = time.time()
			guid = show.getGuid()
			m = hashlib.sha1()
			m.update(guid) 
			key = m.hexdigest()
			ShowKeys.append(str(show.key))
			ShowHashes.append(str(key))
			print i, key, show, " ", time.time() - start_time, "seconds"
			i = i + 1

def findMovieByHash(hashtofind):
	key = MovieKeys[MovieHashes.index(hashtofind)]
	element = server.query(key)
	print element[0].attrib['title']
	server.refreshItem(key)

def findShowByHash(hashtofind):
	key = ShowKeys[ShowHashes.index(hashtofind)]
	element = server.query(key.replace('/children',''))
	print element[0].attrib['title']
	server.refreshItem(key)

start_time = time.time()
print_time = time.time()
filecount = 0
for root, subdirs, files in os.walk(SearchDirectory):
	for file in files:
		if time.time() - print_time >= PeriodicMessageTime:
			print filecount, time.time() - start_time, root
			print_time = time.time()
		dupliate_count = 0
		filename = root+"/"+file
		try:
			if imghdr.what(filename) == 'jpeg':
				try:
					filecount = filecount + 1
					im = Image.open(filename)
					pix = im.load()
					x = pix[im.size[0]-1,im.size[1]-1]
				except IOError as e:
					if "truncated" in str(e):
						print filename
						os.remove(filename)
						regex = re.compile("/?(?P<hash0>[a-zA-Z0-9\-\s\']+)/?(?P<hash1>[a-zA-Z0-9\-\s\']+).bundle")
						file_match = regex.search(root)
						if file_match is not None:
							hash = file_match.group('hash0')+file_match.group('hash1')
							try:
								findMovieByHash(hash)
							except:
								try:
									findShowByHash(hash)
								except:
									print sys.exc_info()[0]
									pass
		except IOError as e:
			if "No such file" in str(e):
				try: os.remove(filename)
				except: 
					print sys.exc_info()[0]
					pass

def genThumbs():
	for section in server.library.sections:
		if not "Misc" in str(section) and not "Unsorted" in str(section):
			start_time = time.time()
			content = section.getContent('all')
			print section, len(content), " ", time.time() - start_time, "seconds"
			for show in content:
				thumb = show.getThumb()
				if not thumb is None:
					start_time = time.time()
					#server.transcodePhoto(128, 200, 0, thumb) #Web
					#server.transcodePhoto(200, 300, 0, thumb) #Web
					server.transcodePhoto(188, 260, 1, thumb) #SamsungTV
					server.transcodePhoto(184, 280, 1, thumb) #SamsungTV
					server.transcodePhoto(184, 268, 1, thumb) #SamsungTV
					server.transcodePhoto(376, 560, 1, thumb) #SamsungTV
					print show, " Thumb ", time.time() - start_time, "seconds ", thumb
				art = show.getArt()
				if not art is None:
					start_time = time.time()
					#server.transcodePhoto(128, 200, 0, art) #Web
					#server.transcodePhoto(256, 256, 0, art) #Web
					#server.transcodePhoto(1280, 720, 0, art) #Web
					server.transcodePhoto(960, 540, 1, art) #SamsungTV
					print show, " Art ", time.time() - start_time, "seconds ", art
				#seasons = show.seasons
				#for season in seasons:
					#thumb = season.getThumb()
					#if not thumb is None:
						#server.transcodePhoto(128, 200, 0, thumb) #Web

genThumbs()

start_time = time.time()
print_time = time.time()
filecount = 0
for root, subdirs, files in os.walk(CacheDirectory):
	for file in files:
		if time.time() - print_time >= PeriodicMessageTime:
			print filecount, time.time() - start_time, root
			print_time = time.time()
		filecount += 1
		filename = root+"/"+file
		atime = os.stat(filename).st_atime
		if time.time() - atime > (60*60*24*7*4):
			print time.ctime(atime), time - atime
			os.remove(filename)

start_time = time.time()
print_time = time.time()
filecount = 0
for root, subdirs, files in os.walk(CacheDirectory):
	for file in files:
		if time.time() - print_time >= PeriodicMessageTime:
			print filecount, time.time() - start_time, root
			print_time = time.time()
		filename = root+"/"+file
		if imghdr.what(filename) == 'jpeg':
			filecount += 1
			im = Image.open(filename)
			try:
				pix = im.load()
				x = pix[im.size[0]-1,im.size[1]-1]
				if im.mode == 'L':
					if x == 128:
						print filename
						os.remove(filename)
				else:
					if x[0] == 128 and x[1] == 128 and x[2] == 128:
						print filename
						os.remove(filename)
			except IOError as e:
				if "truncated" in str(e):
					print filename
					os.remove(filename)
					
genThumbs()


print "Optimizing"
server.optimize()
time.sleep(5)