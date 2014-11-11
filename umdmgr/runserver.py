#!/usr/bin/env python

#standard imports
import getopt	
import sys

def usage():
	print "v, verbose logs everything"
	#print "l, loop, loops every 10s"
	print "e, errors, print errors"
		
if __name__ == "__main__":
	#project imports
	from server import umdserver
	from server import gv
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "vle", ["verbose", "loop", "errors"]) 
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
		else:
			print "option '%s' not recognised"%opt
			#assert False, 'option not recognised'
			usage() 
			sys.exit(1)
	if gv.loud:
		print "Starting in verbose mode"
	umdserver.main()
