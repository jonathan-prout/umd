#!/usr/bin/env python

#standard imports
import getopt	
import sys
import threading


def usage():
	print "v, verbose logs everything"
	#print "l, loop, loops every 10s"
	print "e, errors, print errors"
		
if __name__ == "__main__":
	#project imports
	from server import umdserver
	from server import gv
	from helpers import mysql
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "vlesn", ["verbose", "loop", "errors", "suppress","snail"]) 
	except getopt.GetoptError, err:
		print str(err)	
		print "error in arguments"
		usage()                          
		sys.exit(2) 
	#verbose = False
	loop = False
	
	for opt, arg in  opts:
	
		if opt in ("-v", "--verbose"):
			gv.loud = True
		elif opt in ("-e", "--errors"):
			errors_in_stdout = True
		elif opt in ("-s", "--suppress"):
			gv.suppressEquipCheck = True
		elif opt in ("-n", "--snail"):
			gv.quitWhenSlow = False
		else:
			print "option '%s' not recognised"%opt
			#assert False, 'option not recognised'
			usage() 
			sys.exit(1)
	if gv.loud:
		print "Starting in verbose mode"
		
	gv.sql = mysql.mysql()
	gv.sql.autocommit = True
	#gv.sql.semaphore = threading.BoundedSemaphore(value=10)
	gv.sql.mutex = threading.RLock()
	umdserver.main()
