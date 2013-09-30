#!/usr/bin/python

import os, re, sys
import string,threading,time, Queue, getopt
import equipment_new
import mysql, gv
from gv import log
#gv.loud = False
errors_in_stdout = False


def retrivalList():
    #global gv.sql
    globallist = []
    #request = "select * FROM equipment"
    request = "select id, ip, labelnamestatic FROM equipment"
    
    return  gv.sql.qselect(request)
    """  
    except:
            raise "Oooppp...."
            return NULL
    """
    

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
	threading.Thread.__init__(self)
	self.threadID = threadID
	self.name = name
	self.counter = counter

    def run(self):
        #print "Starting " + self.name
        backgroundworker()
        log( "Exiting " + self.name)


def beginthreads():
    log( "Starting %s threads..."% gv.bg_worker_threads)
    gv.threads = []
    for t in range(gv.bg_worker_threads):
	    name = "myThread-%s"% t
	    bg = myThread(t, name, t)
	    bg.daemon = True
	    gv.threads.append(bg)
	    bg.start()

def start():
	#Begin background worker threads
	beginthreads()
	try:
	    pick, tot = gv.parity.split('/')
	    pick = int(pick)
	except:
	    print "'%s' is not a fraction." % gv.parity
	    pick = 1
	    tot = 1
	counter = 1
	tot = int(tot)
	for equipmentID, ip, name in retrivalList():
		if counter == pick:
		    #print equipmentID, ip, name
		    if name == "IP Gridport":
			    newird = equipment_new.IPGridport(int(equipmentID), ip, name)
		    else:
			    newird = equipment_new.GenericIRD(int(equipmentID), ip, name)
		    gv.addEquipment(newird)
		if counter == tot:
		    counter = 1
		else:
		    counter += 1
	#print gv.equipmentDict
	for equipmentID in gv.equipmentDict.keys():
		gv.ThreadCommandQueue.put((determine_type, [equipmentID, False]))
    
def determine_type(args):
	t = "ERROR"
	equipmentID, autostart = args
	try:
		Type = gv.equipmentDict[equipmentID].determine_type()
	except:
		Type = "OFFLINE"
	
	ip = gv.equipmentDict[equipmentID].ip
	
	name = gv.equipmentDict[equipmentID].name
	
	if  "TT1260" in Type:
		newird = equipment_new.TT1260(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		gv.addEquipment(newird)
		t = "TT1260"
		
	elif  "RX1290" in Type:
		newird = equipment_new.RX1290(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		gv.addEquipment(newird)
		t = "RX1290"
		
	elif "Rx8000"in Type:
		newird = equipment_new.RX8200(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		gv.addEquipment(newird)
		t = "Rx8200"
		
	elif "TVG420"in Type:
		newird = equipment_new.TVG420(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		gv.addEquipment(newird)
		t = "TVG420"
		newird.lastRefreshTime = 0
	elif "IP Gridport"in Type:
	    	newird = equipment_new.IPGridport(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		gv.addEquipment(newird)
		t = "IP Gridport"
		
	elif Type == "OFFLINE":	
		t = "OFFLINE"
		gv.equipmentDict[equipmentID].offline = True
	query = "UPDATE equipment SET model_id ='%s' WHERE id ='%i'"%(t, equipmentID)
	if gv.loud:
		print "IRD " + str(equipmentID) + " is a " + t
	gv.sql.qselect(query)
	if autostart:
		if gv.threadJoinFlag == False:
			if Type != "OFFLINE":
				gv.ThreadCommandQueue.put((refresh, equipmentID))

def refresh(equipmentID):
    min_refresh_time = 5 #Force 5 seconds between refreshes
    try:
	t = gv.equipmentDict[equipmentID].lastRefreshTime
    except:
	t = 0
    
    if not gv.equipmentDict[equipmentID].get_offline():
	if t > (time.time() - min_refresh_time): 
	    time.sleep(max(0, (min_refresh_time - (time.time() - t) )))
	try:
	    gv.equipmentDict[equipmentID].refresh()
	except:
	    gv.equipmentDict[equipmentID].set_offline()

    if not gv.equipmentDict[equipmentID].get_offline():		    
	e = gv.equipmentDict[equipmentID]
	updatesql = e.updatesql()
	msg = gv.sql.qselect(updatesql)
	
	#except: raise "gv.sql ERRROR"
	
	# process channel
	updatechannel = e.getChannel()
	re = gv.sql.qselect(updatechannel)
	
	gv.equipmentDict[equipmentID].lastRefreshTime = time.time()
	gv.hit(equipmentID)
	# Add itself to end of queue
	if gv.threadJoinFlag == False:
	    gv.ThreadCommandQueue.put((refresh, equipmentID))

        
def backgroundworker():
	#import time
	item = 1
	
	gotdata = True
	while gv.threadTerminationFlag == False:
	    #while not gv.ThreadCommandQueue.empty():
	    #print "still in while"
	    #func, data = gv.ThreadCommandQueue.get()
	    
	    try:
		    func, data = gv.ThreadCommandQueue.get()
		    gotdata = True
		    
	    except Queue.Empty:
		    time.sleep(0.1)
		    gotdata = False
		    
	    if gotdata:
		    #print  "Processing Item %s" % item
		    func(data)
    
		    #print "processed a thred command!s"
		    gv.ThreadCommandQueue.task_done()
		    item +=1
	thread.exit()


def cleanup():
    import sys
    gv.sql.close()
    gv.threadTerminationFlag = True
    sys.exit(0)

def main():
    log( "Started " )
    time1 = time.time()

    start()
    #backgroundworker()
    gv.ThreadCommandQueue.join()
    log( "Types determined. Took %s seconds. Begininng main loop. Press CTRL C to quit"% (time.time() - time1))
    for k in gv.equipmentDict.keys():
		gv.ThreadCommandQueue.put((refresh, k))
    
    """
    for i in range(5):
	time1 = time.time()
	

	#backgroundworker()
	gv.ThreadCommandQueue.join()
	log( "Took %s seconds. "% (time.time() - time1))
    
	
    
    for k in gv.equipmentDict.keys():
	    print gv.equipmentDict[k].updatesql()
	    print gv.equipmentDict[k].getChannel()
    """
    loopcounter = 0
    while gv.threadTerminationFlag == False:
	try:
	
	    time.sleep(30)
	    if loopcounter > 5:
		inactives = gv.get_inactive()
		if gv.loud:
		    print inactives
		try:
		    for item in inactives:
			if gv.loud:
			    print "Restarting UMD for ID %s" %item
			gv.ThreadCommandQueue.put((determine_type, [item, True]))
		except TypeError:
		    pass
	    loopcounter += 1
	    if loopcounter > 19: # Restart all threads every 5 minutes
		gv.threadJoinFlag = True
		if gv.loud:
			print "Joining Queue"
		gv.ThreadCommandQueue.join()
		"""
		if gv.loud:
			print "Joining Threads"
		
		gv.threadTerminationFlag = True
		for thread in gv.threads:
		    thread.join(5)
		    if thread.isAlive(): #becomes is_alive() in later Python versions
			if gv.loud:
			    print "Thread Timed out. :("
		
		"""    
		if gv.loud:
			print "Resuming Threads"
		gv.threadJoinFlag = False
		gv.threadTerminationFlag = False
		"""
		for thread in gv.threads:
		    thread.run()
		"""
		for k in gv.equipmentDict.keys():
		    gv.ThreadCommandQueue.put((refresh, k))
		loopcounter = 0
	except KeyboardInterrupt:
	    print "Quitting"
	    cleanup()
	    break

    

	
def usage():
	print "v, verbose logs everything"
	print "l, loop, loops every 10s"
	print "e, errors, print errors"
	print "p, gv.parity Type a fraction IE 1/2 will use only odd number equipment and 2/2 will use even"
		
if __name__ == "__main__":
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "vlep:", ["verbose", "loop", "errors", "parity="]) 
	except getopt.GetoptError, errr:
		print str(errr)	
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
	    elif opt in ("-p", "--parity"):
		gv.parity = arg
	    else:
		print opt
		assert False, 'option not recognised' 
	try:
	    a,b = gv.parity.split('/')
	except:
	    print "'%s' is not a fraction." % gv.parity
	    sys.exit(2)
	
	if gv.loud:
		print "Starting in verbose mode"
	main()