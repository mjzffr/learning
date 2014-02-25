#!/usr/bin/env python2

import sys
import socket
# I'm not using urlib on purpose, for learning

def parse_input():
	usage = "Usage:" + sys.argv[0] + " URL. URL must start with 'http://'"
	if '-h' in sys.argv or 'help' in sys.argv:
		print usage
	elif len(sys.argv) == 2 and sys.argv[1].startswith('http://'):
		# remove http://
		urlString = sys.argv[1].replace('http://', '', 1)
		# URL object stores domain and path separately
		url = URL(urlString)
		download(url)
	else: 
		print usage


def download(url):
	''' downloads file pointed to by URL object '''

	# TODO
	# create an INET, STREAMing socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# connect to the web server on port 80: this socket will be used
	# for one request and one reply and then be destroyed
	s.connect(url.domain, 80)

def get_progress_str():
	pass


class URL:
	def __init__(self, urlString):
		self.original = urlString
		# split into domain and path
		urlParts = urlString.split('/', 1)
		self.domain = urlParts[0]
		if len(urlParts) == 2:
			self.path = urlParts[1]
		else:
			self.path = ''

	def __str__(self):
		return 'domain: [' + self.domain + ']; path: [' + self.path + ']'

if __name__ == "__main__":
	parse_input()