#!/usr/bin/env python

from __future__ import print_function
import getopt
import sys
import datetime
import threading


def usage():
	print("v, verbose logs everything")
	print("l, loop, loops every 10s")
	print("e, errors, print errors")


if __name__ == '__main__':
	from client import umdclient
	from helpers import mysql
	from client import gv
	sql = mysql.mysql()

	sql.semaphore = threading.BoundedSemaphore(value=1)
	sql.mutex = threading.RLock()
	gv.sql = sql
	gv.display_server_status = "Starting"
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "vlet:", ["verbose", "loop", "errors", "test"]) 
	except getopt.GetoptError as err:
			
		print("error in arguments {}".format(err))
		usage()                          
		sys.exit(2) 

	loop = False
	test = None
	for opt, arg in  opts:
	
		if opt in ("-v", "--verbose"):
			#loud = True
			gv.loud = True
		elif opt in ("-l", "--loop"):
			loop = True
		elif opt in ("-t", "--test"):
			test = arg
		elif opt in ("-e", "--errors"):
			errors_in_stdout = True
		else:
			print(opt)
			assert False, 'option not recognised' 

	if gv.loud:
		print("Starting in verbose mode")



			
	now = datetime.datetime.now()
	if gv.loud:
		print("starting " + now.strftime("%d-%m-%Y %H:%M:%S"))
	""" Begins main loop"""
	umdclient.main(loop, test)
	now = datetime.datetime.now()
	if gv.loud:
		print("Done " + now.strftime("%d-%m-%Y %H:%M:%S"))
		
	
	umdclient.shutdown(0)
