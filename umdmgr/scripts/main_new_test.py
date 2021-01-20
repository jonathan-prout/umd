#!/usr/bin/python

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
import os, re, sys
import string,threading,time, queue
import equipment_new
import mysql, gv




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


def start():
	
	#Begin background worker threads
	print("Starting %s threads..."% gv.bg_worker_threads)
	for t in range(gv.bg_worker_threads):
		bg = threading.Thread(None,target=backgroundworker, args=[])
		bg.daemon = True
		gv.threads.append(bg)
		bg.start()
	

	for equipmentID, ip, name in retrivalList():
		#print equipmentID, ip, name
		newird = equipment_new.GenericIRD(int(equipmentID), ip, name)
		gv.addEquipment(newird)
	#print gv.equipmentDict
	for equipmentID in list(gv.equipmentDict.keys()):
		gv.ThreadCommandQueue.put((determine_type, equipmentID))
    
def determine_type(equipmentID):
    try:
        Type = gv.equipmentDict[equipmentID].determine_type()
    except:
	Type = "OFFLINE"
    print("IRD " + str(equipmentID) + " is a " + Type)
    ip = gv.equipmentDict[equipmentID].ip
    name = gv.equipmentDict[equipmentID].name
    query = "UPDATE equipment SET model_id ='%s' WHERE id ='%i'"%(Type, equipmentID)
    gv.sql.qselect(query)
    if Type == "TT1260":
        newird = equipment_new.TT1260(equipmentID, ip, name)
        gv.addEquipment(newird)
    elif Type == "RX1290":
        newird = equipment_new.RX1290(equipmentID, ip, name)
        gv.addEquipment(newird)
    elif Type == "RX8200":
        newird = equipment_new.RX8200(equipmentID, ip, name)
        gv.addEquipment(newird)
    elif Type == "OFFLINE":	
		gv.equipmentDict[equipmentID].offline = True


def refresh(equipmentID):
    
    if not gv.equipmentDict[equipmentID].offline:
		gv.equipmentDict[equipmentID].refresh()
		
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
		#if gv.programTerminationFlag == False:
		#    gv.ThreadCommandQueue.put((refresh, equipmentID))

        
def backgroundworker():
	import time
	item = 1
	
	gotdata = True
	while gv.programTerminationFlag == False:
	#while not gv.ThreadCommandQueue.empty():
		#print "still in while"
		#func, data = gv.ThreadCommandQueue.get()
		
		try:
			func, data = gv.ThreadCommandQueue.get()
			gotdata = True
			
		except queue.Empty:
			time.sleep(0.1)
			gotdata = False
			
		if gotdata:
			#print  "Processing Item %s" % item
			func(data)

			#print "processed a thred command!s"
			gv.ThreadCommandQueue.task_done()
			item +=1


def cleanup():
    import sys
    
    gv.programTerminationFlag = True
    gv.ThreadCommandQueue.join()
    gv.sql.close()
    sys.exit(0)

def main():
    "Started at " + time.strftime("%H:%M:%S")
    time1 = time.time()

    start()
    #backgroundworker()
    gv.ThreadCommandQueue.join()
    print("Types determined. Took %s seconds. Begininng main loop. Press CTRL C to quit"% (time.time() - time1))
    
    for k in list(gv.equipmentDict.keys()):
		gv.ThreadCommandQueue.put((refresh, k))
    
    
    for i in range(2):
	time1 = time.time()
	for k in list(gv.equipmentDict.keys()):
	    gv.ThreadCommandQueue.put((refresh, k))

	#backgroundworker()
	gv.ThreadCommandQueue.join()
	print("Took %s seconds. "% (time.time() - time1))
    
    """
    
    for k in gv.equipmentDict.keys():
	    print gv.equipmentDict[k].updatesql()
	    print gv.equipmentDict[k].getChannel()
    
    while gv.programTerminationFlag == False:
	try:
	
	    time.sleep(15)
	    inactives = gv.get_inactive()
	    try:
		for item in inactives:
		    gv.ThreadCommandQueue.put(determine_type, item)
	    except TypeError:
		pass
	except KeyboardInterrupt:
	    print "Quitting"
	    cleanup()
	    break
    """
    

	
if __name__ == '__main__':
    main()
    cleanup()