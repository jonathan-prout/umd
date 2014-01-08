#!/usr/bin/python

import os, re, sys
import string,threading,time, Queue, getopt
import equipment_new
import mysql, gv

#gv.loud = False
errors_in_stdout = False


def retrivalList():
    #global gv.sql
    globallist = []
    #request = "select * FROM equipment"
    request = "select id, ip, labelnamestatic FROM equipment"
    
    return  gv.sql.qselect(request)


class myThread (threading.Thread):
	myQ = gv.ThreadCommandQueue
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
		self.running = False

		
	def run(self):
		#print "Starting " + self.name
		try:
			self.running = True
			backgroundworker(self.myQ)
		except Exception as e:
			print e
		finally:
			self.running = False
		print "Exiting " + self.name


		
def crashdump():
	import pickle, time
	print "UMD MANAGER HAS MADE AN ERROR AND WILL NOW CLOSE"
	filepath = "/var/www/programming/server/"
	filename = filepath + "server-crashdump-%s.pickle"% time.strftime("%Y_%m_%d_%H_%M_%S")
	cmd = "UPDATE `UMD`.`management` SET `value` = 'OFFLINE_ERROR' WHERE `management`.`key` = 'current_status';"
	gv.sql.qselect(cmd)
	cmdq = []
	while not gv.ThreadCommandQueue.empty():
		cmdq.append(gv.ThreadCommandQueue.get())
	objs = [ cmdq, gv.equipmentDict, gv.exceptions]
	with open(filename, "w") as fobj:
		pickle.dump(objs, fobj)
	#ecit with error status
	cleanup(1)

def beginthreads():
	print "Starting %s threads..."% gv.bg_worker_threads
	gv.threads = []
	for t in range(gv.bg_worker_threads):
		if t in range(gv.offlineCheckThreads):
			name = "offlineCheck-%s"% t
		else:
			name = "normalThread-%s"% t
		bg = myThread(t, name, t)
		bg.daemon = True
		gv.threads.append(bg)
		if t in range(gv.offlineCheckThreads):
			bg.myQ = gv.offlineQueue
		bg.start()
	

def start():
	#Begin background worker threads
	beginthreads()
	

	for equipmentID, ip, name in retrivalList():
		#print equipmentID, ip, name
		if name == "IP Gridport": #NOT SNMP
			newird = equipment_new.IPGridport(int(equipmentID), ip, name)
		#elif "NS2000" in name: #Method not supported yet
		#	newird = equipment_new.NS2000(int(equipmentID), ip, name)
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
	
	# Equipment Types without subtype
	simpleTypes = {
		"TT1260":equipment_new.TT1260,
		"RX1290":equipment_new.RX1290,
		"DR5000":equipment_new.DR5000,
		"TVG420":equipment_new.TVG420,
		"IP Gridport":equipment_new.IPGridport,
		
	}
	
	for key in simpleTypes.keys():
		if  key in Type:
			newird = simpleTypes[key](equipmentID, ip, name)
			newird.lastRefreshTime = 0
			gv.addEquipment(newird)
			t = key
			break
	# Equipment Type with subtype
	if "Rx8000"in Type:
		newird = equipment_new.RX8200(equipmentID, ip, name)
		subtype = newird.determine_subtype()
		if subtype == "RX8200-4RF":
		    newird = equipment_new.RX8200_4RF(equipmentID, ip, name)
		elif subtype == "RX8200-2RF":
		    newird = equipment_new.RX8200_2RF(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		gv.addEquipment(newird)
		t = "Rx8200"
		
	elif "NS2000"in Type:
		newird = equipment_new.NS2000(equipmentID, ip, name)
		subtype = newird.determine_subtype()
		if subtype == "NS2000_WEB":
		    newird = equipment_new.NS2000_WEB(equipmentID, ip, name)
		elif subtype == "NS2000_SNMP":
		    newird = equipment_new.NS2000_SNMP(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		gv.addEquipment(newird)
		t = "NS2000"
		
	elif Type == "OFFLINE":	
		t = "OFFLINE"
		gv.equipmentDict[equipmentID].offline = True
	query = "UPDATE equipment SET model_id ='%s' WHERE id ='%i'"%(t, equipmentID)
	
	if gv.loud:
		print "IRD " + str(equipmentID) + " is a " + t
	gv.sql.qselect(query)
	u = 'Online'
	if t == 'OFFLINE':
	    u = 'Offline'
	query = "UPDATE `UMD`.`status` SET `aspectratio` = '',`status` = '%s', `ebno` = '', `frequency` = '', `symbolrate` = '', `asi` = '', `sat_input` = '', `bissstatus` = '', `videoresolution` = '', `framerate` = '', `videostate` = '', `asioutmode` = '', `framerate` = '',`muxbitrate` = '', `muxstate` = '' WHERE `status`.`id` = '%i'"%(u, equipmentID)
	gv.sql.qselect(query)
	if autostart:
		if gv.threadJoinFlag == False:
			if Type != "OFFLINE":
				gv.ThreadCommandQueue.put((refresh, equipmentID))

def refresh(equipmentID):
	currentEquipment = gv.equipmentDict[equipmentID]
	import time
	try:
		t = currentEquipment.lastRefreshTime
	except:
		t = 0
	
	if not currentEquipment.get_offline():
		while t > (time.time() - currentEquipment.min_refresh_time()):
			#if gv.loud: print "sleeping %s seconds" % max(0, (gv.min_refresh_time - (time.time() - t) ))
			sleepytime = min(max(0, (currentEquipment.min_refresh_time() - (time.time() - t) )), 1)
			time.sleep(sleepytime)
		
	try:
		currentEquipment.refresh()
	except:
		currentEquipment.set_offline()
	
	if not currentEquipment.get_offline():		    
		
		updatesql = currentEquipment.updatesql()
		msg = gv.sql.qselect(updatesql)
		
		#except: raise "gv.sql ERRROR"
		
		# process channel
		updatechannel = currentEquipment.getChannel()
		re = gv.sql.qselect(updatechannel)
		
		currentEquipment.lastRefreshTime = time.time()
		try:
			
			currentEquipment.refreshjitter = time.time() - currentEquipment.excpetedNextRefresh 
		except: pass
		
		
		currentEquipment.excpetedNextRefresh = time.time() + currentEquipment.min_refresh_time()
		gv.hit(equipmentID)
		# Add itself to end of queue
		if gv.threadJoinFlag == False:
			gv.ThreadCommandQueue.put((refresh, equipmentID))

        
def backgroundworker(myQ):
	import time
	item = 1
	
	gotdata = True
	while gv.threadTerminationFlag == False:
		#while not gv.ThreadCommandQueue.empty():
		#print "still in while"
		#func, data = gv.ThreadCommandQueue.get()
		try:
			func, data = myQ.get()
			gotdata = True
			
		except Queue.Empty:
			time.sleep(0.1)
			gotdata = False
			
		if gotdata:
			#print  "Processing Item %s" % item
			func(data)
		
			#print "processed a thred command!s"
			myQ.task_done()
			item +=1
	#thread.exit()


def cleanup(exit_status=0):
	import sys
	try:
		gv.threadTerminationFlag = True
		for thread in gv.threads:
			thread.join(1)
		if exit_status == 0:
			cmd = "UPDATE `UMD`.`management` SET `value` = 'OFFLINE' WHERE `management`.`key` = 'current_status';"
			gv.sql.qselect(cmd)
		gv.sql.close()
	except Exception as e:
		print "%s error during shutdown"%type(e)
		exit_status = 1
	finally:
		sys.exit(exit_status)

def main(debugBreak = False):
	print "Started at " + time.strftime("%H:%M:%S")
	finishedStarting = False
	cmd = "UPDATE `UMD`.`management` SET `value` = 'STARTING' WHERE `management`.`key` = 'current_status';"
	gv.sql.qselect(cmd)
	cmd = "UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'up_since';"% time.strftime("%Y %m %d %H:%M:%S")
	gv.sql.qselect(cmd)
	
	time1 = time.time()
	
	start()
	#backgroundworker()
	gv.ThreadCommandQueue.join()
	print "Types determined. Took %s seconds. Begininng main loop. Press CTRL C to quit"% (time.time() - time1)
	for k in gv.equipmentDict.keys():
		gv.ThreadCommandQueue.put((refresh, k))
	
	"""
	for i in range(5):
	time1 = time.time()
	
	
	#backgroundworker()
	gv.ThreadCommandQueue.join()
	print "Took %s seconds. "% (time.time() - time1)
	
	
	
	for k in gv.equipmentDict.keys():
		print gv.equipmentDict[k].updatesql()
		print gv.equipmentDict[k].getChannel()
	"""
	loopcounter = 0
	while gv.threadTerminationFlag == False:
		try:
			time.sleep(30)
			if not finishedStarting:
				cmd = "UPDATE `UMD`.`management` SET `value` = 'RUNNING' WHERE `management`.`key` = 'current_status';"
				gv.sql.qselect(cmd)
			finishedStarting = True
			
			if loopcounter > 3:
				inactives = gv.get_inactive()
				if gv.loud:
					print inactives
				try:
					for item in inactives:
						if gv.loud:
							print "Restarting UMD for ID %s" %item
						gv.offlineQueue.put((determine_type, [item, True]))
				except TypeError:
					pass
			loopcounter += 1
			if loopcounter > 10: # Restart all threads every 5 minutes
				try:
					while 1:
						gv.offlineQueue.get_nowait() #Truncate Queue
				except Queue.Empty:
					pass
					
				
				if gv.loud:
					print "Joining Queue"
				gv.threadJoinFlag = True
				gv.ThreadCommandQueue.join()
		
				for k in gv.equipmentDict.keys():
					if gv.equipmentDict[k].get_offline():
						gv.offlineQueue.put((determine_type, k))
					else:
						gv.ThreadCommandQueue.put((refresh, k))
				loopcounter = 0
				if gv.loud:
					print "Resuming Threads"
				gv.threadJoinFlag = False
				gv.threadTerminationFlag = False
			
			if loopcounter > 2:
				oncount = 0
				offcount = 0
				runningThreads = 0
				stoppedThreads = 0
				
				jitterlist = []
				for equipmentID in gv.equipmentDict.keys():
					try:
						if gv.equipmentDict[equipmentID].get_offline():
							offcount += 1
						else:
							oncount += 1
							jitterlist.append(gv.equipmentDict[equipmentID].refreshjitter)
							if gv.loud:
								print "%s: %s"%(equipmentID, gv.equipmentDict[equipmentID].refreshjitter)
					except: pass
				def avg(L):
					return float(sum(L)) / len(L)
				for t in gv.threads:
					try:
						if t.running:
							runningThreads += 1
						else:
							stoppedThreads += 1
					except:
						stoppedThreads += 1
				if gv.loud:
					print "Refresh statistics loop %s"% loopcounter
					print "Minimum refresh time %s seconds" % gv.min_refresh_time
					print "MAX: %s MIN: %s AVG:%s "%(max(jitterlist)+ gv.min_refresh_time, min(jitterlist)+ gv.min_refresh_time, avg(jitterlist)+ gv.min_refresh_time)
					print "%s stopped threads. %s running threads"%(stoppedThreads, runningThreads)
				mj = float(min(jitterlist))
				xj = float(max(jitterlist))
				aj = float(avg(jitterlist))
				gv.sql.qselect("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'min_jitter';" %mj )
				gv.sql.qselect("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'max_jitter';" %xj  )
				gv.sql.qselect("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'avg_jitter';" %aj)
				gv.sql.qselect("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'equipment_online';" %oncount    )
				gv.sql.qselect("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'equipment_offline';"%offcount)
				gv.sql.qselect("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'last_self_check';"% time.strftime("%Y %m %d %H:%M:%S"))
				gv.sql.qselect("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'errors';"%len(gv.exceptions))   
				gv.sql.qselect("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'running_threads';"%runningThreads)
				
				
				new_poll_time = gv.sql.qselect("SELECT * FROM `management` WHERE `key` LIKE 'min_poll_time'")
				try:
					fpoll_time = float(new_poll_time[0][1])
					if fpoll_time > 0:
						gv.min_refresh_time = fpoll_time
				except:
					pass
				if gv.loud:
					print "Min refresh time now %s"%gv.min_refresh_time
				assert oncount > offcount, "More equipment off than on. Most likely an error there"
				assert len(gv.exceptions) < 20, "Program has errors"
				assert aj < 15, "Program is running slowly so quitting"
				assert gv.programChrashed == False, "Program Crashed flag has been raised so quitting"
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
				if debugBreak:
					print "Leaving loop"
					return
				
				"""
				for thread in gv.threads:
					thread.run()
				"""
	
		except KeyboardInterrupt:
			print "Quitting"
			cleanup()
			break
		
		except Exception as e:
			gv.exceptions.append(e)
			print "%s Error."%type(e)
			crashdump()
		

    

	
def usage():
	print "v, verbose logs everything"
	print "l, loop, loops every 10s"
	print "e, errors, print errors"
		
if __name__ == "__main__":
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "vle", ["verbose", "loop", "errors"]) 
	except getopt.GetoptError, err:
		print str(err)	
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
		else:
			print opt
			assert False, 'option not recognised' 

	if gv.loud:
		print "Starting in verbose mode"
	main()