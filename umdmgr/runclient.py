#!/usr/bin/env python

import getopt
import sys
import datetime

def usage():
	print "v, verbose logs everything"
	print "l, loop, loops every 10s"
	print "e, errors, print errors"
	
if __name__ == '__main__':
	from client import umdclient
	
	from client import gv
	
	gv.display_server_status = "Starting"
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "vle", ["verbose", "loop", "errors"]) 
	except getopt.GetoptError, errr:
		print str(err)	
		print "error in arguments"
		usage()                          
		sys.exit(2) 
	#verbose = False
	loop = False
	
	for opt, arg in  opts:
	
		if opt in ("-v", "--verbose"):
			#loud = True
			gv.loud = True
		elif opt in ("-l", "--loop"):
			loop = True
		elif opt in ("-e", "--errors"):
			errors_in_stdout = True
		else:
			print opt
			assert False, 'option not recognised' 

	if gv.loud:
		print "Starting in verbose mode"



			
	now = datetime.datetime.now()
	if gv.loud:
		print "starting " + now.strftime("%d-%m-%Y %H:%M:%S")
	umdclient.main(loop)
	now = datetime.datetime.now()
	if gv.loud:
		print "Done " + now.strftime("%d-%m-%Y %H:%M:%S")
		
	
	umdclient.shutdown(0)