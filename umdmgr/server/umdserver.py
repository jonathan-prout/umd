#!/usr/bin/python

from __future__ import print_function
from __future__ import absolute_import
from future import standard_library

import server
import server.equipment.ericsson
import server.equipment.ateme
import server.equipment.ateme_titan
import server.equipment.tvips
import server.equipment.omneon
from helpers.logging import log, logerr

standard_library.install_aliases()
from builtins import str
from builtins import range
import os, re, sys
import string, threading, time, getopt
import queue
import multiprocessing
import random
import gc
from server import equipment
from server import gv
from server import bgtask
from helpers import alarm, snmp
from helpers import debug
import traceback
from pympler import muppy
from pympler import summary
import atexit
snmp.gv = gv  # in theory we don't want to import explictly the server's version of gv

from helpers import mysql

# gv.loud = False
errors_in_stdout = False


def retrivalList(_id=None):
	globallist = []
	if _id:
		request = "select id, ip, labelnamestatic, model_id, subequipment FROM equipment WHERE id='%d'" % _id
	else:
		request = "select id, ip, labelnamestatic, model_id, subequipment FROM equipment"

	return gv.sql.qselect(request)


class myThread(threading.Thread):
	myQ = gv.ThreadCommandQueue

	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
		self.running = False

	def __repr__(self):
		return f"<self.name, self.threadID, self.counter>"

	def run(self):

		try:
			self.running = True
			backgroundworker(self.myQ)
		except Exception as e:
			logerr(callingInstance=self)
			log(f"Error {e} in thread", self, alarm.level.Critical)
		finally:
			self.running = False
		log("Exiting " + self.name, self, alarm.level.Debug)


class dbthread(myThread):
	myQ = gv.dbQ

	def run(self):

		try:
			self.running = True
			dbworker(self.myQ)
		except Exception as e:
			logerr(callingInstance=self)
			log(f"Error {e} in thread", self, alarm.level.Critical)
		finally:
			self.running = False
		log("Exiting " + self.name, self, alarm.level.Debug)


def getEquipmentDict():
	equipmentDict = {}
	for k, v in gv.equipmentDict.items():
		try:
			equipmentDict[k] = v.serialize()
		except:
			continue


def crashdump():
	log("UMD MANAGER HAS MADE AN ERROR AND WILL NOW CLOSE", "crashdump", alarm.level.Emergency)
	try:
		gv.threadTerminationFlag.value = True
		gv.threadJoinFlag = True
		import pickle, time

		filepath = ""
		filename = filepath + "server-crashdump-%s.pickle" % time.strftime("%Y_%m_%d_%H_%M_%S")
		cmd = "UPDATE `UMD`.`management` SET `value` = 'OFFLINE_ERROR' WHERE `management`.`key` = 'current_status';"
		gv.sql.qselect(cmd)
		cmdq = [[], [], []]

		while not gv.ThreadCommandQueue.empty():
			cmdq[0].append(gv.ThreadCommandQueue.get(False))
		while not gv.dbQ.empty():
			cmdq[1].append(gv.dbQ.get(False))
		while not gv.CheckInQueue.empty():
			cmdq[2].append(gv.dbQ.get(False))

		equipmentDict = getEquipmentDict()
		objs = [cmdq, equipmentDict, gv.exceptions]

		with open(filename, "w") as fobj:
			pickle.dump(objs, fobj)
	# ecit with error status
	except Exception as e:
		log("crashdump failed, because of an error", "crashdump", alarm.level.Critical)
		logerr("crashdump")

	finally:
		cleanup(1)


def beginthreads():
	gv.threads = []

	log("Starting %s offline check subprocesses..." % gv.offlineCheckThreads, "beginthreads", alarm.level.Debug)
	for t in range(gv.offlineCheckThreads):
		bg = multiprocessing.Process(target=backgroundProcessWorker,
		                             args=(gv.offlineQueue, gv.dbQ, gv.CheckInQueue, gv.threadTerminationFlag))
		gv.threads.append(bg)
		bg.start()
	log("Starting %s worker subprocesses..." % gv.bg_worker_threads, "beginthreads", alarm.level.Debug)
	for t in range(gv.offlineCheckThreads, gv.bg_worker_threads + gv.offlineCheckThreads):
		bg = multiprocessing.Process(target=backgroundProcessWorker,
		                             args=(gv.ThreadCommandQueue, gv.dbQ, gv.CheckInQueue, gv.threadTerminationFlag))
		gv.threads.append(bg)
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
	# Begin background worker threads
	if not gv.threads:
		beginthreads()
	# Equipment Types 
	simpleTypes = {
		"TT1260": server.equipment.ericsson.TT1260,
		"RX1290": server.equipment.ericsson.RX1290,
		"DR5000": server.equipment.ateme.DR5000,
		"TVG420": server.equipment.tvips.TVG420,
		"IP Gridport": server.equipment.omneon.IPGridport,
		"Rx8200": server.equipment.ericsson.RX8200,
		"Titan": server.equipment.ateme_titan.Titan

	}
	log("Getting equipment", "start", alarm.level.OK)
	for equipmentID, ip, name, model_id, subequipment in retrivalList(_id):
		query = "SELECT `id` from `status` WHERE `status`.`id` ='%d'" % equipmentID
		if len(gv.sql.qselect(query)) == 0:
			query = "REPLACE INTO `UMD`.`status` SET `id` ='%d'" % equipmentID
		gv.sql.qselect(query)
		for key in list(simpleTypes.keys()):

			if any(((key in model_id), (key in name))):
				newird = simpleTypes[key](int(equipmentID), ip, name, subequipment)
				break

		else:
			newird = equipment.generic.GenericIRD(int(equipmentID), ip, name, subequipment)
		gv.addEquipment(newird)
	log("Determining types", "start", alarm.level.OK)
	for currentEquipment in list(gv.equipmentDict.values()):
		gv.ThreadCommandQueue.put(("determine_type", currentEquipment.serialize()), block=True)


def dbworker(myQ):
	import time
	item = 1

	gotdata = True
	while gv.threadTerminationFlag.value == False:
		try:
			cmd = myQ.get(timeout=1)
			gotdata = True

		except queue.Empty:
			time.sleep(0.1)
			gotdata = False

		if gotdata:
			gv.sql.qselect(cmd)
			myQ.task_done()


class dispatcher(myThread):
	def run(self):
		STAT_INIT = 0
		STAT_SLEEP = 1
		STAT_READY = 2
		STAT_INQUEUE = 3
		STAT_CHECKEDOUT = 4
		STAT_STUCK = 5
		while gv.threadTerminationFlag.value == False:
			if gv.threadJoinFlag == False:
				for equipmentID, instance in gv.equipmentDict.items():
					if gv.threadJoinFlag:
						break
					try:
						put_block = True
						if instance.checkout.getStatus() in [STAT_INIT, STAT_READY, STAT_STUCK]:
							if isinstance(instance, server.equipment.generic.GenericIRD):
								task = "determine_type"
								myq = gv.ThreadCommandQueue
							else:
								if instance.get_offline():
									task = "determine_type"
									myq = gv.offlineQueue
									put_block = False
								else:
									task = "refresh"
									myq = gv.ThreadCommandQueue
							myq.put((task, gv.equipmentDict[equipmentID].serialize()), block=put_block)
							instance.checkout.enqueue()
					except queue.Full:
						time.sleep(0.1)
						continue
			else:
				time.sleep(0.1)
		log("Exiting " + self.name, self, alarm.level.Debug)


class checkin(myThread):
	def run(self):
		myq = gv.CheckInQueue
		while gv.threadTerminationFlag.value == False:
			try:
				data = myq.get(timeout=1)
				myq.task_done()
				if "equipmentId" in data:
					gv.gotCheckedInData = True
					equipmentID = data["equipmentId"]
					try:
						assert (not gv.equipmentDict[equipmentID].get_offline())
						gv.equipmentDict[equipmentID].deserialize(data)
					except AssertionError:  # Reinstance when checking in offline equip
						gv.equipmentDict[equipmentID] = bgtask.deserialize(data, keepData=False)
					except TypeError:  # Equipment Type Changed
						gv.equipmentDict[equipmentID] = bgtask.deserialize(data, keepData=False)
					gv.equipmentDict[equipmentID].checkout.checkin()

				else:
					gv.gotCheckedInData = False
					log(f"checkin fail {data}", self, alarm.level.Critical)
				del data
			except queue.Empty:
				gv.gotCheckedInData = False
				time.sleep(0.1)


def backgroundProcessWorker(myQ, dbQ, checkInQueue, endFlag):
	""" Entry point for sub process """
	from . import gv
	from helpers import mysql, logging
	myproc = multiprocessing.current_process()
	logging.startlogging(f"/var/log/umd/umdserver_proc{myproc}.log")
	gv.dbQ = dbQ
	gv.CheckInQueue = checkInQueue
	if not gv.sql:
		gv.sql = mysql.mysql()
		gv.sql.autocommit = True
		# gv.sql.semaphore = threading.BoundedSemaphore(value=10)
		gv.sql.mutex = multiprocessing.RLock()

	backgroundworker(myQ, endFlag)


def backgroundworker(myQ, endFlag=None):
	import time
	from . import bgtask
	import sys
	import traceback
	import multiprocessing
	myproc = "processs %s" % multiprocessing.current_process()
	item = 1
	log("Started", myproc, alarm.level.Info)
	def getTerminated():
		try:
			return endFlag.value
		except (AttributeError, OSError):  # This fails in the profiler
			return gv.threadTerminationFlag.value

	gotdata = True
	while not getTerminated():
		try:
			func, data = myQ.get(timeout=1)
			gotdata = True

		except queue.Empty:
			time.sleep(0.1)
			gotdata = False

		if gotdata:

			error = None
			try:
				bgtask.funcs[func](data)
			except KeyboardInterrupt:
				log("caught KeyboardInterrupt and is closing", myproc, alarm.level.Info)
				return

			except Exception as e:
				logerr(myproc)
				try:
					message = e.message
				except AttributeError:
					message = "no message"
				log("Error in  ignored. error type is %s and message is %s\n" % (e, message), myproc, alarm.level.Warning)
				sys.stderr.flush()

			finally:
				myQ.task_done()


			item += 1





@atexit.register
def cleanup(exit_status=0):
	try:
		_prexit = gv.preexit
	except:
		gv.preexit = False
		_prexit = False
	if not _prexit:
		import sys
		try:

			gv.threadTerminationFlag.value = True
			log("Set termination flag", "cleanup", alarm.level.Info)
			time.sleep(1)
			log("Joining threads and waiting for subprocesses", "cleanup", alarm.level.Info)
			for thread in gv.threads:
				thread.join(1)
				print(".", end=' ')
			if exit_status == 0:
				cmd = "UPDATE `UMD`.`management` SET `value` = 'OFFLINE' WHERE `management`.`key` = 'current_status';"
				gv.sql.qselect(cmd)

			gv.sql.close()
			gv.preexit = True
		except Exception as e:
			logerr("cleanup")
			log("%s error during shutdown" % type(e), "cleanup", alarm.level.Info)
			exit_status = 1
		finally:
			sys.exit(exit_status)


def main(debugBreak=False):
	log("Started", "main", alarm.level.Ok)
	finishedStarting = False
	cmd = "UPDATE `UMD`.`management` SET `value` = 'STARTING' WHERE `management`.`key` = 'current_status';"
	gv.sql.qselect(cmd)
	cmd = "UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'up_since';" % time.strftime(
		"%Y %m %d %H:%M:%S")
	gv.sql.qselect(cmd)

	time1 = time.time()

	start()
	# backgroundworker()
	gv.ThreadCommandQueue.join()
	gv.CheckInQueue.join()
	log("Types determined. Took %s seconds. Begininng main loop. Press CTRL C to %s" % (
	time.time() - time1, ["quit", "enter debug console"][gv.debug]), "main", alarm.level.Info)
	if gv.debug:


		all_objects = muppy.get_objects()
		gv.mem_sum1 = summary.summarize(all_objects)

	log("Starting dispatch", "main", alarm.level.OK)
	gv.threads[gv.dispatcherThread].start()


	loopcounter = 0
	while gv.threadTerminationFlag.value == False:
		try:

			if not finishedStarting:
				cmd = "UPDATE `UMD`.`management` SET `value` = 'RUNNING' WHERE `management`.`key` = 'current_status';"
				gv.dbQ.put(cmd)
			finishedStarting = True

			loopcounter += 1
			if loopcounter > 10:  # Restart all threads every 10 minutes
				loopcounter = 0

				log("Stopping dispatcher", "main", alarm.level.Debug)
				gv.threadJoinFlag = True
				gv.ThreadCommandQueue.join()
				log("Garbage Collection", "main", alarm.level.Debug)
				collected = gc.collect()
				log("collected %s objects. Resuming" % collected, "main", alarm.level.Debug)
				gv.threadJoinFlag = False
			if loopcounter > 2:
				oncount = 0
				offcount = 0
				runningThreads = 0
				stoppedThreads = 0
				tallyDict = {}

				def tally(key):
					if key in tallyDict:
						tallyDict[key] += 1
					else:
						tallyDict[key] = 1

				jitterlist = []
				lateCounter = 0
				onTimeCounter = 0
				for equipmentID in list(gv.equipmentDict.keys()):
					try:
						if gv.equipmentDict[equipmentID].get_offline():
							offcount += 1
						elif isinstance(gv.equipmentDict[equipmentID], equipment.generic.GenericIRD):
							offcount += 1
						else:
							oncount += 1
							jitter = gv.equipmentDict[equipmentID].checkout.jitter
							jitterlist.append(jitter)
							severity = alarm.level.OK
							if float(jitter) > 5:
								severity = alarm.level.Info
							if float(jitter) > 10:
								severity = alarm.level.Warning
							if float(jitter) > 30:
								severity = alarm.level.Major
							log("Refresh Jitter %s: %s" % (equipmentID, jitter), "main", severity)



					except:
						continue
					statuses = {
						0: "STAT_INIT",
						1: "STAT_SLEEP",
						2: "STAT_READY",
						3: "STAT_INQUEUE",
						4: "STAT_CHECKEDOUT",
						5: "STAT_STUCK"
					}
					if hasattr(gv.equipmentDict[equipmentID], "checkout"):
						try:
							tally(statuses[gv.equipmentDict[equipmentID].checkout.getStatus()])
						except KeyError:
							tally("KeyError")

						if gv.equipmentDict[equipmentID].checkout.timestamp < time.time() - gv.equipmentDict[
							equipmentID].min_refresh_time():
							if gv.loud:
								print("%d %f seconds late with status %s" % (equipmentID,
								                                             time.time() - gv.equipmentDict[
									                                             equipmentID].min_refresh_time() -
								                                             gv.equipmentDict[
									                                             equipmentID].checkout.timestamp,
								                                             statuses[gv.equipmentDict[
									                                             equipmentID].checkout.getStatus()]))
							lateCounter += 1
						else:
							onTimeCounter += 1
					else:
						tally("missing")

				def avg(L):
					return float(sum(L)) / len(L)

				for t in gv.threads:
					try:
						if t.is_alive():
							runningThreads += 1
						else:
							stoppedThreads += 1
					except:
						stoppedThreads += 1
				if gv.loud:
					log("Refresh statistics loop %s" % loopcounter, "main", alarm.level.Debug)
					log("Minimum refresh time %s seconds" % gv.min_refresh_time, "main", alarm.level.Debug)
					try:
						log("MAX: %s MIN: %s AVG:%s " % (
							log(jitterlist) + gv.min_refresh_time, min(jitterlist) + gv.min_refresh_time,
							avg(jitterlist) + gv.min_refresh_time), "main", alarm.level.Debug)
					except (ValueError, TypeError):
						log("Could not get jitter", "main", alarm.level.Warning)
					log("%s stopped threads. %s running threads" % (stoppedThreads, runningThreads), "main",
					    [alarm.level.Debug, alarm.level.Warning][stoppedThreads>0])
					for k, v in tallyDict.items():
						log("%d in status %s" % (v, k), "main", alarm.level.Debug)
					for k in list(statuses.values()):  # returns names
						try:
							v = tallyDict[k]
						except KeyError:
							v = 0
						gv.dbQ.put(
							"UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = '%s';" % (v, k))
					if gv.loud:
						print("%d / %d late" % (lateCounter, lateCounter + onTimeCounter))
				mj = float(min(jitterlist))
				xj = float(max(jitterlist))
				aj = float(avg(jitterlist))
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'min_jitter';" % mj)
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'max_jitter';" % xj)
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'avg_jitter';" % aj)
				gv.dbQ.put(
					"UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'equipment_online';" % oncount)
				gv.dbQ.put(
					"UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'equipment_offline';" % offcount)
				gv.dbQ.put(
					"UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'last_self_check';" % time.strftime(
						"%Y %m %d %H:%M:%S"))
				gv.dbQ.put("UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'errors';" % len(
					gv.exceptions))
				gv.dbQ.put(
					"UPDATE `UMD`.`management` SET `value` = '%s' WHERE `management`.`key` = 'running_threads';" % runningThreads)

				if gv.debug:
					all_objects = muppy.get_objects()
					mem_sum2 = summary.summarize(all_objects)
					diff = summary.get_diff(gv.mem_sum1, mem_sum2)
					summary.print_(diff)

				new_poll_time = gv.sql.qselect("SELECT * FROM `management` WHERE `key` LIKE 'min_poll_time'")
				try:
					fpoll_time = float(new_poll_time[0][1])
					if fpoll_time > 0:
						gv.min_refresh_time = fpoll_time
				except:
					pass
				if gv.loud:
					log("Min refresh time now %s" % gv.min_refresh_time, "main", alarm.level.Debug)
				possibleErrors = []
				possibleErrors.append((oncount < offcount, "More equipment off than on. Most likely an error there"))
				possibleErrors.append((len(gv.exceptions) > 20, "Program has errors"))
				if gv.quitWhenSlow:
					possibleErrors.append((lateCounter > (onTimeCounter * 3), "Program is running slowly so quitting"))
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
					log("Leaving loop", "main", alarm.level.Info)
					return

				"""
				for thread in gv.threads:
					thread.run()
				"""

			time.sleep(30)
		except KeyboardInterrupt:
			if gv.debug:
				gv.threadJoinFlag = True
				log("Pausing to debug", "main", alarm.level.Debug)
				debug.debug_breakpoint()
			else:
				log("Quitting due to Keyboard Interrupt", "main", alarm.level.Info)
				cleanup()
				break
		except AssertionError as e:
			logerr("main")
			if gv.debug:

				gv.threadJoinFlag = True
				log("Pausing to debug because of %s" % e.message, "main", alarm.level.Debug)
				debug.debug_breakpoint()
			else:
				log("Program Self Check has caused program to quit.", "main", alarm.level.Critical)

				log("Offline Equipment:", "main", alarm.level.Warning)
				for equipmentID in list(gv.equipmentDict.keys()):
					try:
						if gv.equipmentDict[equipmentID].get_offline():
							eq = gv.equipmentDict[equipmentID]
							log(eq.name.ljust(10, " ") + eq.modelType.ljust(10, " ") + eq.ip, "main", alarm.level.Critical)
					except:
						continue
				log("errors:", "main", alarm.level.Critical)
				log(gv.exceptions, "main", alarm.level.Debug)
				crashdump()
		except Exception as e:
			logerr("main")
			log("Other error of type %s" % type(e), "main", alarm.level.Critical)
			gv.exceptions.append((e, traceback.format_tb(sys.exc_info()[2])))
			try:
				message = e.message
			except:
				message = ""

			if gv.debug:
				gv.threadJoinFlag = True
				log("Pausing to debug", "main", alarm.level.Debug)
				debug.debug_breakpoint()
			else:
				crashdump()
