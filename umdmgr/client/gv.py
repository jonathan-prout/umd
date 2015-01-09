# UMD MANAGER CLIENT
from helpers import mysql
from helpers import rwlock
import threading

threadTerminationFlag = False
programTerminationFlag = False
display_server_status = "Unknown"
loud = True

#mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
#mysql.mysql.mutex = threading.RLock()
sql = mysql.mysql()
equip = {}
labelcache = {}
matrixes = []
matrixCapabilities = {}
threads = []
equipDBLock = threading.RLock()
streamcodes = None
mvID = {}


def getEquipByName(name):
	if name:
		for k,v in equip.iteritems():
			if v.isCalled(name):
				return k
		
	
	return 0

def mtxLookup(name, level = "SDI"):
	"""Lookup source from destination. Returns equip ID int or None """
	try:
		mxes = matrixCapabilities[level]
	except KeyError:
		return None
	srcName = ""
	for mtx in mxes:
		srcName = mtx.sourceNameFromDestName(name)
		if srcName:
			break
	return srcName
	
