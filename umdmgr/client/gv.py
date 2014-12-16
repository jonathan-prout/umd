# UMD MANAGER CLIENT


threadTerminationFlag = False
programTerminationFlag = False
display_server_status = "Unknown"
loud = True
from helpers import mysql
import threading
#mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
#mysql.mysql.mutex = threading.RLock()
sql = mysql.mysql()
equip = {}
labelcache = {}
matrixes = []
matrixCapabilities = {}



gv.mvID = {}


def getEquipByName(name):
	for k,v in equip.iteritems():
		if v.isCalled(name):
			return k
	
	
	return 0

def mtxLookup(name, level):
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
	