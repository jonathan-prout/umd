#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
import urllib.request, urllib.parse, urllib.error
import httplib2
import sys
#from taskscript import debug, die
def debug(stuff):
	import gv
	gv.log(stuff)

def die(stuff):
	print("\n".join(stuff))
	import sys
	sys.exit(1)

def get( ip, port, addr, username="", password="", timeout = 10):
	"""
	ip as string, port as int addr string 
	returns response as dictionary, content as string
	# use when uri separate from address
	"""
	http = httplib2.Http(timeout=timeout)
	method = 'GET'
	if password != "":
		http.add_credentials(username, password)
	url = 'http://{}:{}/{}'.format(ip, port, addr);

	headers = {'Accept': '*',
				'Content-Type': 'application/vnd.ipgp+xml',
				'User-Agent':	'IPGP Player'}
	
	
	
	response, content = http.request(url, method, headers=headers)
	"""
	try:
		
	except:
		die(["HTTP Error with " + ip])
	"""
	return response, content


	
	
def geturl(url, username="", password="", timeout=10):
	"""
	ip as string, port as int addr string do_not_call_machine_test_on_timeout boolean
	returns response as dictionary, content as string
	# use when is complete url passed.
	"""
	
	

	http = httplib2.Http(timeout = timeout)
	method = 'GET'
	
	if password != "":
		http.add_credentials(username, password)

	headers = {'User-Agent':	'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Trident/4.0)'}


	#response, content = http.request(url, method, headers=headers)

	# noinspection PyBroadException
	try:
		response, content = http.request(url, method, headers=headers)
	except Exception:

		die(["HTTP Error with " + url])
	return response, content

	
def getcache_new( ip, port, addr, cache_max_age='120'):
	"""uses sqlite to speed up caching
	# Sometimes a get task from the MediaGrid can take several seconds to complete
	# This can be a problem for interractivity
	# This function reduces that by enabling caching of some features"""
	import sqlhelper
	import time
	import os
	url = 'http://' + ip + ':' + port + '/' + addr
	urlcacheobj = sqlhelper.urlcache()
	urlcacheobj.cache_max_age = cache_max_age
	
	while urlcacheobj.busy(url):
		#If another thread is accessing this url, wait for it to time out before doing anything
		time.sleep(0.1)
	
	
	if urlcacheobj.available(url):
		# Newer than cache timeout.
		# Open cache and return that
		#debug("Returning cached file")
		#print "returning cacched file"
		content = urlcacheobj.get(url)
		response = {
			'status': '200',
			'location': url,
			'cached': 'true'
			}
	else:
		urlcacheobj.setbusy(url)
		response, content = geturl(url)
		if response['status'] == '200':
			urlcacheobj.put(url, content)
		else:
			urlcacheobj.deletewhere("url", url)
	return response, content
		
def getcache( ip, port, addr, cache_max_age='120'):
	"""
	Depreciated
	ip as string, port as int addr string cache_max_age integer
	returns response as dictionary, content as string
	# Sometimes a get task from the MediaGrid can take several seconds to complete
	# This can be a problem for interractivity
	# This function reduces that by enabling caching of some features
	"""
	
	import time
	import os
	string = addr.split("/")
	cachedir = "cache/"
	if not os.path.exists(cachedir):
		os.mkdir(cachedir)
	cachefile = cachedir + "cachefile." + ip
	for part in string:
		cachefile += "."
		cachefile += part
	cachefile += ".xml"
	url = 'http://' + ip + ':' + port + '/' + addr
	try:
		cachecreationtime = os.path.getmtime(cachefile)
	except (IOError, OSError):
		cachecreationtime = 0
	cacheFileRead = False
	if cachecreationtime > (time.time() - int(cache_max_age)):
		# Newer than cache timeout.
		# Open cache and return that
		#debug("Returning cached file")
		#print "returning cacched file"
		try:
			fileobject = open(cachefile)
			content = fileobject.read()
			response = {
				'status': '200',
				'location': url,
				'cached': 'true'
				}
			cacheFileRead = True
		except IOError:
			pass
		
	else:
		# This ensures that subsequent calls to this function
		# do not generate unneccesary HTTP requests
		# while the file is building
		try:
			file = open(cachefile, 'w')
			file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
			file.write('<Waiting />')
		finally:
			file.close()
		#debug("Getting new file for " + url)
		#print "getting new file"
		# Close file while processing. 
		#debug(url)
		response, content = geturl(url)
		#debug(response)
		if response['status'] == '200':
			try:
				file = open(cachefile, 'w')
				file.write(content)
			finally:
				file.close()
		
	return response, content

def post(ip, port, addr, body="", username="", password="", timeout = 10):
	"""
	ip as string, port as int addr body as string 
	returns response as dictionary, content as string
	"""
	http = httplib2.Http(timeout=timeout)
	method = 'POST'
	method = 'GET'
	if password != "":
		http.add_credentials(username, password)
	url = 'http://' + ip + ':' + port + '/' + addr;
	headers = {'Accept': '*',
				'Content-Type': 'application/vnd.ipgp+xml'}


	response, content = http.request(url, method, headers=headers, body=body)

	return response, content

def put( ip, port, addr, body):
	"""
	ip as string, port as int addr body as string 
	returns response as dictionary, content as string
	"""
	http = httplib2.Http()
	debug = 'false'
	method = 'PUT'
	
	url = 'http://' + ip + ':' + port + '/' + addr;
	if debug == 'true':
		print(url)
		print(body)
	headers = {'Content-Type': 'application/vnd.ipgp+xml'}


	response, content = http.request(url, method, body=str(body), headers=headers)

	return response, content


def delete(ip, port, addr):
	"""
	ip as string, port as int addr  as string 
	returns response as dictionary, content as string
	"""
	http = httplib2.Http()
	method = 'DELETE'

	url = 'http://' + ip + ':' + port + '/' + addr;
	headers = {'Accept': '*',
				'Content-Type': 'application/vnd.ipgp+xml'}


	response, content = http.request(url, method, headers=headers)

	return response, content


def replace( location, body):
	"""
	url as string body as string 
	returns response as dictionary, content as string
	"""
	# delete then put at address
	urlstring = location.split("/")
	ipport = urlstring[2]
	baseaddr = urlstring[3]
	try:
		tailaddr = urlstring[4]
	except (IndexError, TypeError):
		tailaddr = ""
	 
	# baseaddr and tailaddr ie "http://10.72.0.5:9998/players/SINK-2"
	# returns ['http:', '', '10.72.0.5:9998', 'players', 'SINK-2']
	# SO         0       1    2                  3          4
	
	http = httplib2.Http()
	
	method = 'PUT'

	url = 'http://' + ipport + '/' + baseaddr + '/' + tailaddr
	
	debug(url)
	debug(body)
	headers = {'Content-Type': 'application/vnd.ipgp+xml'}
	
	delresponse, delcontent = http.request(url, 'DELETE', headers=headers)
	if 'status' in delresponse:
		if (delresponse['status'] == '404'):
			debug("Could not delete, the file as the server says it doesn't exist. Maybe the file finished playing?")
			response = delresponse
			content = delcontent
		

		elif (delresponse['status'] == '200'):
			# 200 means created, so file deleted
			# So lets PUT the updated stream
			debug("Player deleted, creating new player")
			url = 'http://' + ipport + '/' + baseaddr 
			response, content = http.request(url, 'PUT', body=str(body), headers=headers)
		
		else:			
			debug("Error replacing stream!")
			debug(delresponse)
			response = delresponse
			content = delcontent
			#die(zip(response, "----", content))
	else:
		debug("Bad output from server when replacing sream")
		debug(delresponse)
		response = '0'
		content = '0'

	

	return response, content

def deleteurl(addr):
	"""
	url as string string 
	returns response as dictionary, content as string
	"""
	http = httplib2.Http()
	method = 'DELETE'

	url = addr
	headers = {'Accept': '*',
				'Content-Type': 'application/vnd.ipgp+xml'}

	debug(url)
	response, content = http.request(url, method, headers=headers)

	return response, content

if __name__ == '__main__':
	#Call from command line
	method = str(sys.argv[1])
	ip = str(sys.argv[2])
	port = str(sys.argv[3])
	addr = str(sys.argv[4])
	
	if method == 'GET':
		response, content = get( ip, port, addr)
	elif method == 'PUT':
		body = str(sys.argv[5])
		response, content = put( ip, port, addr, body)
	elif method == 'POST':
		body = str(sys.argv[5])
		response, content = put( ip, port, addr, body)
	elif method == 'DELETE':
		body = str(sys.argv[5])
		response, content = put( ip, port, addr, body)
	print(content)		
	"""
	if response.has_key('status'):
		if (response['status'] == '200'):
			print content
		else:
			print response['status']
	else:
		print "Cannot connect"
"""
