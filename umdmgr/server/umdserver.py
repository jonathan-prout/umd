#!/usr/bin/python

import os, re, sys
import string,threading,time, Queue, getopt
import equipment
import gv
from helpers import snmp
snmp.gv = gv #in theory we don't want to import explictly the server's version of gv

from helpers import mysql
#gv.loud = False
errors_in_stdout = False




def retrivalList(_id = None):
	#global gv.sql
	globallist = []
	#request = "select * FROM equipment"
	if _id:
		request =  "select id, ip, labelnamestatic, model_id FROM equipment WHERE id='%d'"%_id
	else:
		request = "select id, ip, labelnamestatic, model_id FROM equipment"
	
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
	#filepath = "/var/www/programming/server/"
	filepath = ""
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
	

def start(_id=None):
	#Begin background worker threads
	beginthreads()
	# Equipment Types 
	simpleTypes = {
		"TT1260":equipment.ericsson.TT1260,
		"RX1290":equipment.ericsson.RX1290,
		"DR5000":equipment.ateme.DR5000,
		"TVG420":equipment.tvips.TVG420,
		"IP Gridport":equipment.omneon.IPGridport,
		"Rx8200":equipment.ericsson.RX8200,
	
	}
	if gv.loud:
		print "Getting equipment"
	for equipmentID, ip, name, model_id in retrivalList(_id):
		#print equipmentID, ip, name
		query = "SELECT `id` from `status` WHERE `status`.`id` ='%d'"%equipmentID
		if len(gv.sql.qselect(query)) == 0:
			query = "REPLACE INTO `UMD`.`status` SET `id` ='%d'"%equipmentID
		gv.sql.qselect(query)
		for key in simpleTypes.keys():
		
			if any( ( ( key in model_id), (key in name) ) ):
				newird = simpleTypes[key](int(equipmentID), ip, name)
				break
		#elif "NS2000" in name: #Method not supported yet
		#	newird = equipment_new.NS2000(int(equipmentID), ip, name)
		else:
			newird = equipment.generic.GenericIRD(int(equipmentID), ip, name)
		gv.addEquipment(newird)
	#print gv.equipmentDict
	if gv.loud:
		print "Determining types"
	for equipmentID in gv.equipmentDict.keys():
		gv.ThreadCommandQueue.put((determine_type, [equipmentID, False]))

def determine_type(args):
	t = "ERROR"
	equipTypeStr = "OFFLINE"
	equipmentID, autostart = args
	try: #remove from offline equip list if it's in there
		gv.offlineEquip.remove(equipmentID)
	except ValueError:
		pass
	if not all( (gv.suppressEquipCheck, (not isinstance(gv.equipmentDict[equipmentID], equipment.generic.GenericIRD ) ) ) ):
		try:
			equipTypeStr = gv.equipmentDict[equipmentID].determine_type()
		except:
			equipTypeStr = "OFFLINE"
	
	ip = gv.equipmentDict[equipmentID].ip
	
	name = gv.equipmentDict[equipmentID].name
	# Equipment equipTypeStrs without subtype
	simpleTypes = {
		"TT1260":equipment.ericsson.TT1260,
		"RX1290":equipment.ericsson.RX1290,
		"DR5000":equipment.ateme.DR5000,
		"TVG420":equipment.tvips.TVG420,
		"IP Gridport":equipment.omneon.IPGridport
		
	}
		
	
	for key in simpleTypes.keys():
		if  any( ( (key in equipTypeStr), isinstance(gv.equipmentDict[equipmentID], simpleTypes[key]) ) ):
			newird = simpleTypes[key](equipmentID, ip, name)
			newird.lastRefreshTime = 0
			gv.addEquipment(newird)
			t = key
			break
		
	# Equipment equipTypeStr with subtype
	if any( ( ("Rx8000"in equipTypeStr), isinstance(gv.equipmentDict[equipmentID], equipment.ericsson.RX8200) ) ):
		newird = equipment.ericsson.RX8200(equipmentID, ip, name)
		subtype = newird.determine_subtype()
		if subtype == "RX8200-4RF":
		    newird = equipment.ericsson.RX8200_4RF(equipmentID, ip, name)
		elif subtype == "RX8200-2RF":
		    newird = equipment.ericsson.RX8200_2RF(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		gv.addEquipment(newird)
		t = "Rx8200"
		
	elif  any( ( ("NS2000"in equipTypeStr), isinstance(gv.equipmentDict[equipmentID], equipment.novelsat.NS2000) ) ):
		newird = equipment.novelsat.NS2000(equipmentID, ip, name)
		subtype = newird.determine_subtype()
		if subtype == "NS2000_WEB":
		    newird = equipment.novelsat.NS2000_WEB(equipmentID, ip, name)
		elif subtype == "NS2000_SNMP":
		    newird = equipment.novelsat.NS2000_SNMP(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		gv.addEquipment(newird)
		t = "NS2000"
		
	elif equipTypeStr == "OFFLINE":	
		t = "OFFLINE"
		gv.equipmentDict[equipmentID].offline = True
	query = "UPDATE equipment SET model_id ='%s' WHERE id ='%i'"%(t, equipmentID)
	
	if gv.loud:
		print "IRD " + str(equipmentID) + " is a " + t
	gv.sql.qselect(query)
	u = 'Online'
	if t == 'OFFLINE':
	    u = 'Offline'
	query = "UPDATE `UMD`.`status` SET `aspectratio` = '',`status` = '%s', `ebno` = '', `frequency` = '', `symbolrate` = '', `asi` = '', `sat_input` = '', `castatus` = '', `videoresolution` = '', `framerate` = '', `videostate` = '', `asioutencrypted` = '', `framerate` = '',`muxbitrate` = '', `muxstate` = '' WHERE `status`.`id` = '%i'"%(u, equipmentID)
	gv.sql.qselect(query)
	if autostart:
		if gv.threadJoinFlag == False:
			if equipTypeStr != "OFFLINE":
				gv.ThreadCommandQueue.put((refresh, equipmentID))

def refresh(equipmentID):
	currentEquipment = gv.equipmentDict[equipmentID]
	import time
	try:
		t = currentEquipment.lastRefreshTime
	except:
		t = 0
	
	if not currentEquipment.get_offline():
		if t > (time.time() - currentEquipment.min_refresh_time()):
			#if gv.loud: print "sleeping %s seconds" % max(0, (gv.min_refresh_time - (time.time() - t) ))
			#sleepytime = min(max(0, (currentEquipment.min_refresh_time() - (time.time() - t) )), 1)
			if gv.threadJoinFlag == False:
				gv.ThreadCommandQueue.put((refresh, equipmentID))
			sleepytime = 0.1
			time.sleep(sleepytime)
			return 
		
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
	else:
		updatesql = "UPDATE `UMD`.`status` SET `aspectratio` = '',`status` = 'Offline', `ebno` = '', `frequency` = '', `symbolrate` = '', `asi` = '', `sat_input` = '', `castatus` = '', `videoresolution` = '', `framerate` = '', `videostate` = '', `asioutencrypted` = '', `framerate` = '',`muxbitrate` = '', `muxstate` = '' WHERE `status`.`id` = '%i'"%equipmentID
		gv.sql.qselect(updatesql)
		
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
			error = None
			try:
				func(data)
			except Exception, e:
				error = e	
			
			finally:	
				#print "processed a thred command!s"
				myQ.task_done()
			if error:
				gv.exceptions.append(error)
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
					while 1:
						gv.offlineQueue.get_nowait() #Truncate Queue
						gv.offlineQueue.task_done()
				except Queue.Empty:
					pass
				
				gv.offlineEquip = []
				
				try:
					for item in inactives:
						if gv.loud:
							print "Restarting UMD for ID %s" %item
						if not item in gv.offlineEquip:
							gv.offlineEquip.append(item)
							ip = gv.equipmentDict[item].ip
							name = gv.equipmentDict[item].name
							newird = equipment.generic.GenericIRD(int(item), ip, name)
							gv.addEquipment(newird)
							gv.offlineQueue.put((determine_type, [item, True]))
				except TypeError:
					pass
			loopcounter += 1
			if loopcounter > 10: # Restart all threads every 10 minutes
				try:
					while 1:
						gv.offlineQueue.get_nowait() #Truncate Queue
						gv.offlineQueue.task_done()
				except Queue.Empty:
					pass
				gv.offlineEquip = []
				
				if gv.loud:
					print "Joining Queue"
				gv.threadJoinFlag = True
				try:
					while 1:
						gv.ThreadCommandQueue.get_nowait() #Truncate Queue
						gv.ThreadCommandQueue.task_done()
				except Queue.Empty:
					pass
				gv.ThreadCommandQueue.join()
				for equipmentID in gv.equipmentDict.keys():
					try:
						if gv.equipmentDict[equipmentID].get_offline():
							offcount += 1
						else:
							jitter = float(gv.equipmentDict[equipmentID].refreshjitter)
						jitterlist.append(jitter)
						
						if gv.loud:
							print "%s: %s"%(equipmentID, jitter)
						
						if float(jitter) > 60:
							gv.equipmentDict[equipmentID].set_offline()
							offcount += 1
							if gv.loud:
								print "kicking %s, %s now %s"%(equipmentID, gv.equipmentDict[equipmentID].ip, ["online","offline"][gv.equipmentDict[equipmentID].get_offline()])
						else:
							oncount += 1
					except:
						continue
				for k in gv.equipmentDict.keys():
					if gv.equipmentDict[k].get_offline():
						if not k in gv.offlineEquip:
							ip = gv.equipmentDict[k].ip
							name = gv.equipmentDict[k].name
							newird = equipment.generic.GenericIRD(int(k), ip, name)
							gv.addEquipment(newird)
							gv.offlineQueue.put((determine_type, [k, True]))
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
							
							jitter = gv.equipmentDict[equipmentID].refreshjitter
							jitterlist.append(jitter)
							if gv.loud:
								print "%s: %s"%(equipmentID, gv.equipmentDict[equipmentID].refreshjitter)
							"""
							if float(jitter) > 30:
								gv.equipmentDict[equipmentID].set_offline()
								offcount += 1
							else:
								oncount += 1
							"""
							oncount += 1
							
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
				possibleErrors = []
				possibleErrors.append( (oncount < offcount, "More equipment off than on. Most likely an error there"))
				possibleErrors.append( (len(gv.exceptions) > 20, "Program has errors"))
				possibleErrors.append( (aj > (gv.min_refresh_time * 2 + 10), "Program is running slowly so quitting"))
				possibleErrors.append((gv.programCrashed == True, "Program Crashed flag has been raised so quitting"))
				for case, problemText in possibleErrors:
					if case:
						raise AssertionError(problemText)
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
		except AssertionError as e:
			print "Program Self Check has caused program to quit."
			print ""
			print "%s Error."%str(e)
			
			print "Offline Equipment:"
			for equipmentID in gv.equipmentDict.keys():
				try:
					if gv.equipmentDict[equipmentID].get_offline():
						eq = gv.equipmentDict[equipmentID]
						print eq.name.ljust(10, " ") + eq.modelType.ljust(10, " ") + eq.ip
				except: continue
			print "errors:"
			print gv.exceptions
			crashdump()
		except Exception as e:
			gv.exceptions.append(e)
			print "%s: %s."%(e,str(e))
			crashdump()
		

    

	
