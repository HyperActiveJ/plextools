from season import Season
from episode import Episode
import urllib

class Show(object):
		def __init__(self, element, server):
				self.server = server
				self.type = 'show'
				self.key = element.attrib['key']
				self.title = element.attrib['title']
				self.summary = element.attrib['summary']
				
				self.genres = [e.attrib['tag'] for e in element.findall('.Genre')]
				self.collections = [e.attrib['tag'] for e in element.findall('.Collection')]
				
				self.seasons_ = []
		
						
		def __len__(self):
				""" returns the number of seasons of this show. """
				return len(self.seasons)
		
		def __iter__(self):
				""" iterate over all seasons. """
				for s in self.seasons:
						yield s
		
		def __str__(self):
				return "<Show: %s>" % self.title
		
		def __repr__(self):
				return "<Show: %s>" % self.title
		
		@property
		def seasons(self):
				""" property that returns a list to all seasons of the show. caches it's value after first call. """
				if not self.seasons_:
						element = self.server.query(self.key)
						self.seasons_ = [Season(e, self.server) for e in element if ('type' in e.attrib) and (e.attrib['type'] == 'season')]
						
				return self.seasons_


		def getSeason(self, num):
				""" returns the season with the index number `num` or None if it doesn't exist. """
				return next((s for s in self.seasons if s.index == num), None)

		def getAllEpisodes(self):
				""" returns a list of all episodes of the show independent of seasons. """
				key = '/'.join(self.key.split('/')[:-1]) + '/allLeaves'
				element = self.server.query(key)
				episodes = [Episode(e, self.server) for e in element if ('type' in e.attrib) and (e.attrib['type'] == 'episode')]
				return episodes
		
		def getNextUnwatchedEpisode(self):
				""" returns the episode that follows the last watched episode in the show over 
						all seasons. if all are watched, return None. 
				"""
				key = '/'.join(self.key.split('/')[:-1]) + '/allLeaves'
				element = self.server.query(key)
				
				prev = None
				for e in reversed(element):
						if ('viewCount' in e.attrib) and (e.attrib['viewCount'] == '1'):
								if prev == None:
										return None
								else:
										return Episode(prev, self.server)
						prev = e
				return Episode(element[0], self.server)
				
		def getThumb(self):
			element = self.server.query(self.key.replace('/children',''))
			if 'thumb' in element[0].attrib:
				return element[0].attrib['thumb']
		
		def getArt(self):
			element = self.server.query(self.key.replace('/children',''))
			if 'art' in element[0].attrib:
				return element[0].attrib['art']
			
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
			
		def match(self):
			url = self.key.replace('/children','') + "/matches?agent=com.plexapp.agents.thetvdb&manual=0"
			element = self.server.query(url)
			print element[0].attrib
			if 'name' in element[0].attrib:
				if element[0].attrib['name'] == self.title:
					guid = urllib.quote(element[0].attrib['guid'], safe="")
					name = element[0].attrib['name'].replace(" ", "+")
					path = self.key.replace('/children','') + "/match?guid=" + guid +"&name=" + name + ""
					self.server.putItem(path)
				else:
					print "WARNING - NO MATCH"