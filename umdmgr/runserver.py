#!/usr/bin/env python

# standard imports
from __future__ import print_function
import getopt	
import sys
import threading
import multiprocessing
# project imports
from helpers.logging import startlogging
from server import umdserver
from server import gv
from helpers import alarm, logging, mysql


def usage():
	print("v, verbose logs everything")
	print("e, errors, print errors")

def startdb():
	gv.sql = mysql.mysql()
	gv.sql.gv = gv
	gv.sql.autocommit = True
	gv.sql.mutex = multiprocessing.RLock()

if __name__ == "__main__":
	logging.startlogging("/var/log/umd/umdserver.log")
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "vlesnd", ["verbose", "loop", "errors", "suppress","snail","debug"]) 
	except getopt.GetoptError as err:
		print(str(err))	
		print("error in arguments")
		usage()                          
		sys.exit(2)
	loop = False
	
	for opt, arg in opts:
	
		if opt in ("-v", "--verbose"):
			gv.loud = True
		elif opt in ("-e", "--errors"):
			errors_in_stdout = True
		elif opt in ("-s", "--suppress"):
			gv.suppressEquipCheck = True
		elif opt in ("-n", "--snail"):
			gv.quitWhenSlow = False
		elif opt in ("-d", "--debug"):
			gv.debug = True
		else:
			print("option '%s' not recognised"%opt)
			usage() 
			sys.exit(1)
	if gv.loud:
		logging.MIN_SEVERITY = alarm.level.OK
	else:
		logging.MIN_SEVERITY = alarm.level.Cleared
	logging.log("Starting in verbose mode", "__main__", alarm.level.Debug)
		
	startdb()
	umdserver.main()
