#!/usr/bin/python

import os, re, sys
import string,threading,time, Queue, getopt
import random
import equipment
import gv
import bgtask
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

class dbthread (myThread):
	myQ = gv.dbQ
		
	def run(self):
		#print "Starting " + self.name
		try:
			self.running = True
			dbworker(self.myQ)
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
	t += 1
	bg = dbthread(t, "dbThread0", t)
	bg.daemon = True
	gv.threads.append(bg)
	bg.start()
	t += 1
	bg = dispatcher(t, "dispatcher0", t)
	bg.daemon = True
	gv.threads.append(bg)
	gv.dispatcherThread = t
	t += 1
	bg = checkin(t, "checkin0", t)
	bg.daemon = True
	gv.threads.append(bg)
	bg.start()
	

def start(_id=None):
	#Begin background worker threads
	if not gv.threads:
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
	for currentEquipment in gv.equipmentDict.values():
		gv.ThreadCommandQueue.put((bgtask.determine_type, currentEquipment.serialize()), block = True)
	
def dbworker(myQ):
	import time
	item = 1
	
	gotdata = True
	while gv.threadTerminationFlag == False:
		#while not gv.ThreadCommandQueue.empty():
		#print "still in while"
		#func, data = gv.ThreadCommandQueue.get()
		try:
			cmd = myQ.get(1)
			gotdata = True
			
		except Queue.Empty:
			time.sleep(0.1)
			gotdata = False
			
		if gotdata:
			#print  "Processing Item %s" % item
			gv.sql.qselect(cmd)
	#thread.exit()
class dispatcher(myThread):
	def run(self):
		STAT_INIT = 0
		STAT_SLEEP = 1
		STAT_READY = 2
		STAT_INQUEUE =3
		STAT_CHECKEDOUT = 4
		STAT_STUCK = 5
		while gv.threadTerminationFlag == False:
			if gv.threadJoinFlag == False:
				for equipmentID, instance in gv.equipmentDict.iteritems():
					
					try:
						if instance.checkout.getStatus() in [STAT_INIT, STAT_READY, STAT_STUCK]:
							if isinstance(instance, gv.equipment.generic.GenericIRD):
								task = bgtask.determine_type
								queue = gv.ThreadCommandQueue
							else:
								if instance.get_offline():
									task = bgtask.determine_type
									queue = gv.offlineQueue
								else:
									task = bgtask.refresh
									queue = gv.ThreadCommandQueue
						queue.put((task, gv.equipmentDict[equipmentID].serialize()),0.1)
						instance.checkout.enqueue()
					except Queue.Full:
						continue
			else:
				time.sleep(0.1)

class checkin(myThread):
	def run(self):
		queue = gv.CheckInQueue
		while gv.threadTerminationFlag == False:
			try:
				data = queue.get(0.1)
				if data.has_key("equipmentId"):
					gv.gotCheckedInData = True
					equipmentID = data["equipmentId"]
					try:
						gv.equipmentDict[equipmentID].deserialize(data)
					except TypeError: #Equipment Type Changed
						gv.equipmentDict[equipmentID] = bgtask.deserialize(data)
					gv.equipmentDict[equipmentID].checkout.checkin()
				else:
					gv.gotCheckedInData = False
					print "checkin fail"
					print data
			except Queue.Empty:
				gv.gotCheckedInData = False

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
	for e in gv.equipmentDict.values():
		gv.ThreadCommandQueue.put((bgtask.refresh, e.serialize()))
	
	"""
	for i in range(5):
	time1 = time.time()
	
	
	#backgroundworker()
	gv.ThreadCommandQueue.join()
	print "Took %s seconds. "% (time.time() - time1)
	print "Starting Dispatcher"
	gv.threads[gv.dispatcherThread].start()
	
	
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
				gv.dbQ.put(cmd)
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
							gv.offlineQueue.put((bgtask.determine_type, [item, True]))
				except TypeError:
					pass
			loopcounter += 1
			if loopcounter > 10: # Restart all threads every 10 minutes
				loopcounter = 0
				"""
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
							jitter = float(gv.equipmentDict[equipmentID].checkout.jitter)
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
							gv.offlineQueue.put((bgtask.determine_type, [k, True]))
					else:
						currentEquipment = gv.equipmentDict[k]
						mr = currentEquipment.min_refresh_time() * 10
						nr = random.randint(0, mr)
						currentEquipment.excpetedNextRefresh = time.time() + float(nr) /100 
						gv.ThreadCommandQueue.put((bgtask.refresh, k))
				loopcounter = 0
				
				if gv.loud:
					print "Resuming Threads"
				gv.threadJoinFlag = False
				gv.threadTerminationFlag = False
				"""
			if loopcounter > 2:
				oncount = 0
				offcount = 0
				runningThreads = 0
				stoppedThreads = 0
				tallyDict = {}
				def tally(key):
					if tallyDict.has_key(key):
						tallyDict[key] += 1
					else:
						tallyDict[key] = 1
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
					statuses = {
						0:"STAT_INIT",
						1:"STAT_SLEEP",
						2:"STAT_READY",
						3:"STAT_INQUEUE",
						4:"STAT_CHECKEDOUT",
						5:"STAT_STUCK"
					}
					if hasattr(gv.equipmentDict[equipmentID], "checkout"):
						try:
							tally(statuses[gv.equipmentDict[equipmentID].checkout.getStatus()])
						except KeyError:
							tally("KeyError")
						if gv.loud:
							if gv.equipmentDict[equipmentID].checkout.timestamp < time.time() - gv.equipmentDict[equipmentID].min_refresh_time():
								print "%d %f seconds late with status %s"%(equipmentID, time.time() - gv.equipmentDict[equipmentID].min_refresh_time() - gv.equipmentDict[equipmentID].checkout.timestamp, statuses[gv.equipmentDict[equipmentID].checkout.getStatus()] )
					else:
						tally("missing")
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
					for k,v in tallyDict.iteritems():
						print "%d in status %s"%(v,k)
				mj = float(min(jitterlist))
				xj = float(max(jitterlist))
				aj = float(avg(jitterlist))
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'min_jitter';" %mj )
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'max_jitter';" %xj  )
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'avg_jitter';" %aj)
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'equipment_online';" %oncount    )
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'equipment_offline';"%offcount)
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'last_self_check';"% time.strftime("%Y %m %d %H:%M:%S"))
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'errors';"%len(gv.exceptions))   
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'running_threads';"%runningThreads)
				
				
				new_poll_time = gv.dbQ.put("SELECT * FROM `management` WHERE `key` LIKE 'min_poll_time'")
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
				if gv.quitWhenSlow:
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
		

    

	
