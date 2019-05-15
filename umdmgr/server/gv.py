

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
import equipment.generic
sql = None

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
		return self.equipmentDict.has_key(key)
	
	
	def __repr__(self):
		dictrepr = dict.__repr__(self)
		return '%s(%s)' % (type(self).__name__, dictrepr)
	
	def update(self, *args, **kwargs):
		print 'update', args, kwargs
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v

statDict = {}
sqlUpdateDict = {}
eqLock = threading.RLock()
def addEquipment(eqInstance):
	with eqLock:
		if equipmentDict.has_key(eqInstance.getId()):
			old = equipmentDict.pop(eqInstance.getId())
			del old
		equipmentDict[eqInstance.getId()] = eqInstance
		if isinstance(eqInstance, equipment.generic.GenericIRD):
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
offlineCheckThreads = 2
try:
	cpus = multiprocessing.cpu_count()
except:
	cpus = 1

workers_per_proc = 4
bg_worker_threads = cpus * workers_per_proc 




""" Queues """
ThreadCommandQueue = Queue(bg_worker_threads)
offlineQueue = Queue(offlineCheckThreads)
dbQ =  Queue()
CheckInQueue = Queue()


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

snmp_res = {}
def cachedSNMP(command):
	if not snmp_res.has_key(command):
		snmp_res[command] = sql.qselect(command)
	return snmp_res[command]
