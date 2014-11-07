#!/usr/bin/python

import os, re, sys
import string,threading,time, Queue
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
	#beginthreads()
	

	for equipmentID, ip, name in retrivalList():
		#print equipmentID, ip, name
		if name == "IP Gridport":
			newird = equipment_new.IPGridport(int(equipmentID), ip, name)
		else:
			newird = equipment_new.GenericIRD(int(equipmentID), ip, name)
		gv.addEquipment(newird)
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
		gv.addEquipment(newird)
		t = "TT1260"
		
	elif  "RX1290" in Type:
		newird = equipment_new.RX1290(equipmentID, ip, name)
		gv.addEquipment(newird)
		t = "RX1290"
		
	elif "Rx8000"in Type:
		newird = equipment_new.RX8200(equipmentID, ip, name)
		gv.addEquipment(newird)
		t = "RX8200"
		
	elif "TVG420"in Type:
		newird = equipment_new.TVG420(equipmentID, ip, name)
		gv.addEquipment(newird)
		t = "TVG420"
		
	elif "IP Gridport"in Type:
		t = "IP Gridport"
	elif Type == "OFFLINE":	
		t = "OFFLINE"
		gv.equipmentDict[equipmentID].offline = True
	query = "UPDATE equipment SET model_id ='%s' WHERE id ='%i'"%(t, equipmentID)
	gv.sql.qselect(query)
	if gv.loud:
		print "IRD " + str(equipmentID) + " is a " + t
	if autostart:
		if gv.threadJoinFlag == False:
			if Type != "OFFLINE":
				gv.ThreadCommandQueue.put((refresh, equipmentID))

def refresh(equipmentID):
    
    if not gv.equipmentDict[equipmentID].get_offline():
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
	#while gv.programTerminationFlag == False:
	while not gv.ThreadCommandQueue.empty():
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


def cleanup():
    import sys
    gv.sql.close()
    gv.programTerminationFlag = True
    sys.exit(0)

def main():
    "Started at " + time.strftime("%H:%M:%S")
    time1 = time.time()

    start()
    backgroundworker()
    #gv.ThreadCommandQueue.join()
    print "Types determined. Took %s seconds. Begininng main loop. Press CTRL C to quit"% (time.time() - time1)
    
    #for k in gv.equipmentDict.keys():
    #	gv.ThreadCommandQueue.put((refresh, k))
    
    
    for i in range(4):
	time1 = time.time()
	for k in gv.equipmentDict.keys():
	    gv.ThreadCommandQueue.put((refresh, k))

	backgroundworker()
	#gv.ThreadCommandQueue.join()
	print "Took %s seconds. "% (time.time() - time1)
    
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