""""
SERVER GLOBAL VARIABLES
"""


from __future__ import print_function
from __future__ import absolute_import


# Standard Imports
import collections
import threading 
import datetime 
import time 
#import Queue
from multiprocessing import JoinableQueue as Queue
import multiprocessing
#Project imports 
from helpers import mysql
import server.equipment.generic
sql = None

programCrashed = True

min_refresh_time = 10 #Force 10 seconds between refreshes. Gets overidden by min refresh time parameter on matrix



	


last_refresh_dict = {}
oidDict = {}

equipmentDict = {}
class equipmentStorage(object):
	def __init__(self):
		self.equipmentDict  = {}
		self.rLock = threading.RLock()
		self.semaphore = threading.Semaphore(bg_worker_threads)
	
	def __getitem__(self, key):
		return self.equipmentDict[key]
	
	def __setitem__(self, key, val):
		self.equipmentDict[key] = val
	
	def has_key(self, key):
		return key in self.equipmentDict
	
	
	def __repr__(self):
		dictrepr = dict.__repr__(self)
		return '%s(%s)' % (type(self).__name__, dictrepr)
	
	def update(self, *args, **kwargs):
		print('update', args, kwargs)
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v

statDict = {}
sqlUpdateDict = {}
eqLock = threading.RLock()
def addEquipment(eqInstance):
	with eqLock:
		if eqInstance.getId() in equipmentDict:
			old = equipmentDict.pop(eqInstance.getId())
			del old
		equipmentDict[eqInstance.getId()] = eqInstance
		if isinstance(eqInstance, server.equipment.generic.GenericIRD):
			determined = "undetermined"
		else:
			determined = "determined"
		statDict[eqInstance.getId()] = {"determined":determined,"last action":"addEquipment", "timestamp":time.time()}

programCrashed = False
exceptions = []

"""Keeping track of theads"""

from multiprocessing import Value
offlineEquip = []
threads = []
threadTerminationFlag = Value("i", False)
threadJoinFlag = False
offlineCheckThreads = 8
try:
	cpus = multiprocessing.cpu_count()
except:
	cpus = 1

workers_per_proc = 4
bg_worker_threads = cpus * workers_per_proc 




""" Queues """
SIZE_ThreadCommandQueue = bg_worker_threads*2
ThreadCommandQueue = Queue(SIZE_ThreadCommandQueue)
SIZE_offlineQueue = offlineCheckThreads
offlineQueue = Queue(SIZE_offlineQueue)
SIZE_dbQ = bg_worker_threads
dbQ = Queue(SIZE_dbQ)
SIZE_CheckInQueue = bg_worker_threads
CheckInQueue = Queue(SIZE_dbQ)


gotCheckedInData = False

parity = "1/1"
suppressEquipCheck = False
loud = False
loudSNMP = False
quitWhenSlow = False
logfile = "/var/www/programming/server/server_log.txt"
debug = False
loglock = threading.RLock()


def log(stuff):
	out = "%s: Instance %s: %s \n"%(time.strftime("%Y-%m-d %H:%M:%S"), parity, stuff)
	
	if loud:
		print("%s"%out)
	else:
		loglock.acquire()
		try:
			f = open(logfile, "a")
			f.write(out)
		except:
			print("Could not log stuff!")
			print(out)
		finally:
			f.close()
			loglock.release()


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

colours = {}

snmp_res = {}
def cachedSNMP(command):
	if command not in snmp_res:
		snmp_res[command] = sql.qselect(command)
	return snmp_res[command]
