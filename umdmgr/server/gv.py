

# Standard Imports
import collections
import threading 
import datetime 
import time 
import Queue
#Project imports 
from helpers import mysql

sql = None

min_refresh_time = 10 #Force 10 seconds between refreshes. Gets overidden by min refresh time parameter on matrix


last_refresh_dict = {}
oidDict = {}

equipmentDict = {}
def addEquipment(equipment):		
	equipmentDict[equipment.getId()] = equipment

programCrashed = False
exceptions = []

"""Keeping track of theads"""
ThreadCommandQueue = Queue.Queue()
offlineQueue = Queue.Queue()
offlineEquip = []
threads = []
threadTerminationFlag = False
threadJoinFlag = False
bg_worker_threads =25
offlineCheckThreads = 2
parity = "1/1"
suppressEquipCheck = False
loud = False
logfile = "/var/www/programming/server/server_log.txt"
loglock = threading.RLock()
def log(stuff):
	out = "%s: Instance %s: %s \n"%(time.strftime("%Y-%m-d %H:%M:%S"), parity, stuff)
	
	if loud:
		print "%s"%out
	else:
		loglock.acquire()
		try:
			f = open(logfile, "a")
			f.write(out)
		except:
			print "Could not log stuff!"
			print out
		finally:
			f.close()
			loglock.release()
def hit(equipmentId):
    last_refresh_dict[equipmentId] = time.time()

def get_inactive():
	list_of_timeouts = []
	for k in equipmentDict.keys():
		"""
		if not last_refresh_dict.has_key(k):
		    list_of_timeouts.append(k)
		    
		else:
		    if last_refresh_dict[k] < (time.time() -30):
			list_of_timeouts.append(k)
		"""	
		try:
			if equipmentDict[k].get_offline():
				list_of_timeouts.append(k)
				
		except:
			pass
		
	return list_of_timeouts
