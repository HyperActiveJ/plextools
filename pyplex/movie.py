import urllib

class Movie(object):
		
		def __init__(self, element, server):
				self.server = server
				
				# browse element and extract some information
				self.key = element.attrib['key']
				self.type = 'movie'
				self.title = element.attrib['title']
				self.year = ''
				try:
					self.year = int(element.attrib['year'])
					self.summary = element.attrib['summary']
					self.viewed = ('viewCount' in element.attrib) and (element.attrib['viewCount'] == '1')
					self.offset = int(element.attrib['viewOffset']) if 'viewOffset' in element.attrib else 0
					self.file = element.find('.Media/Part').attrib['file']
				except:
					pass
				
		def __str__(self):
				return "<Movie: %s (%s)>" % (self.title, self.year)
		
		def __repr__(self):
				return "<Movie: %s (%d)>" % (self.title, self.year)
		
		def getGuid(self, x = 0):
			element = self.server.query(self.key.replace('/children',''))
			if 'guid' in element[0].attrib:
				return element[0].attrib['guid']
			else:
				if x < 2:
					print "Retrying", x, self, self.key #, element[0].attrib
					return self.getGuid(x+1)
				else:
					print "failed to get GUID"
					return None

		def getThumb(self):
			element = self.server.query(self.key.replace('/children',''))
			if 'thumb' in element[0].attrib:
				return element[0].attrib['thumb']
		
		def getArt(self):
			element = self.server.query(self.key.replace('/children',''))
			if 'art' in element[0].attrib:
				return element[0].attrib['art']
			
		def match(self):
			return
			url = self.key.replace('/children','') + "/matches?agent=com.plexapp.agents.themoviedb&manual=0"
			element = self.server.query(url)
			print element[0].attrib
			if 'name' in element[0].attrib:
				if element[0].attrib['name'] == self.title:
					guid = urllib.quote(element[0].attrib['guid'], safe="")
					name = element[0].attrib['name'].replace(" ", "+")
					path = self.key.replace('/children','') + "/match?guid=" + guid +"&name=" + name + ""
					print path
					self.server.putItem(path)
				else:
					print "WARNING - NO MATCH"