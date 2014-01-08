
import collections, threading, datetime, time, Queue, mysql


sql = mysql.mysql()
sql.semaphore = threading.BoundedSemaphore(value=10)
sql.mutex = threading.RLock()
min_refresh_time = 10 #Force 5 seconds between refreshes


last_refresh_dict = {}
oidDict = {}

equipmentDict = {}
def addEquipment(equipment):		
	equipmentDict[equipment.getId()] = equipment

programChrashed = False
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
			if equipmentDict[k].offline:
				list_of_timeouts.append(k)
				
		except:
			pass
		
	return list_of_timeouts