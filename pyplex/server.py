from library import Library
from client import Client

import urllib2
import urllib
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XML

class Server(object):
		
		def __init__(self, address, port=32400):
				# TODO: clean up address, remove http:// etc
				
				# remove slash at end of address
				if address[-1] == '/':
						address = address[:-1]
				self.address = address
				self.port = int(port)
				
				
		def execute(self, path):
				if path[0] == '/':
						path = path[1:]
						
				# open url
				try: 
						urllib2.urlopen("http://%s:%d/%s" % (self.address, self.port, path)) 
				except urllib2.URLError, e:
						print e

				
		def query(self, path):
				if path[0] == '/':
						path = path[1:]
						
				# open url and get raw xml data
				try:
						response = urllib2.urlopen("http://%s:%d/%s" % (self.address, self.port, path))
				except urllib2.URLError, e:
						print e
				
				# create element from xml data
				xmldata = response.read()
				element = XML(xmldata)
				return element
		
		def transcodePhoto(self, width, height, upscale, imageUrl):
				imageUrl = urllib.quote("http://127.0.0.1:32400" + imageUrl, safe="")
				if upscale:
					path = "photo/:/transcode?width=%s&height=%s&upscale=%s&url=%s" % (width, height, upscale, imageUrl)
				else:
					path = "photo/:/transcode?width=%s&height=%s&url=%s" % (width, height, imageUrl)
				try:
						response = urllib2.urlopen("http://%s:%d/%s" % (self.address, self.port, path))
				except urllib2.URLError, e:
						print e

		def refreshItem(self, path):
			if path[0] == '/':
				path = path[1:]
			path = path.replace('/children','')
			#print path
			opener = urllib2.build_opener(urllib2.HTTPHandler)
			request = urllib2.Request("http://%s:%d/%s/refresh" % (self.address, self.port, path), data='')
			request.add_header('Content-Type', 'text/xml;charset=utf-8')
			request.get_method = lambda: 'PUT'
			try:
					url = opener.open(request)
			except urllib2.URLError, e:
					print e
					raise
				
				
		def putItem(self, path, data = ''):
			if path[0] == '/':
				path = path[1:]
			path = path.replace('/children','')
			#print path
			opener = urllib2.build_opener(urllib2.HTTPHandler)
			request = urllib2.Request("http://%s:%d/%s" % (self.address, self.port, path), data)
			request.add_header('Content-Type', 'text/xml;charset=utf-8')
			request.get_method = lambda: 'PUT'
			try:
					url = opener.open(request)
			except urllib2.URLError, e:
					print e
					raise
		
		def libraryRefresh(self, turbo = 1):
			path = "/library/sections/all/refresh?trubo=" + str(turbo)
			if path[0] == '/':
						path = path[1:]
			try:
				response = urllib2.urlopen("http://%s:%d/%s" % (self.address, self.port, path))
			except urllib2.URLError, e:
				print e
			
		def cleanBundles(self):
			self.putItem("/library/clean/bundles")
			
		def optimize(self):
			self.putItem("/library/optimize")
		
		def __str__(self):
				return "<Server: %s:%d/>" % (self.address, self.port) 
		
		def __repr__(self):
				return "<Server: %s:%d/>" % (self.address, self.port) 
		
		
		@property
		def library(self):
				elem = self.query("/library")
				return Library(self)
		
		@property
		def clients(self):
				elem = self.query("/clients")
				clist = [Client(e, self) for e in elem]
				return clist

