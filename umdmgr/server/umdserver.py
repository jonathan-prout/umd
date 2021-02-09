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

standard_library.install_aliases()
from builtins import str
from builtins import range
import os, re, sys
import string, threading, time, getopt
import queue
import multiprocessing
import random
import gc
from . import equipment
from . import gv
from . import bgtask
from helpers import snmp
from helpers import debug
import traceback
from pympler import muppy
from pympler import summary
snmp.gv = gv  # in theory we don't want to import explictly the server's version of gv

from helpers import mysql

# gv.loud = False
errors_in_stdout = False


def retrivalList(_id=None):
	# global gv.sql
	globallist = []
	# request = "select * FROM equipment"
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

	def run(self):
		# print "Starting " + self.name
		try:
			self.running = True
			backgroundworker(self.myQ)
		except Exception as e:
			print(e)
		finally:
			self.running = False
		print("Exiting " + self.name)


class dbthread(myThread):
	myQ = gv.dbQ

	def run(self):
		# print "Starting " + self.name
		try:
			self.running = True
			dbworker(self.myQ)
		except Exception as e:
			print(e)
		finally:
			self.running = False
		print("Exiting " + self.name)


def getEquipmentDict():
	equipmentDict = {}
	for k, v in gv.equipmentDict.items():
		try:
			equipmentDict[k] = v.serialize()
		except:
			continue


def crashdump():
	print("UMD MANAGER HAS MADE AN ERROR AND WILL NOW CLOSE")
	try:
		gv.threadTerminationFlag.value = True
		gv.threadJoinFlag = True
		import pickle, time

		# filepath = "/var/www/programming/server/"
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
		print("crashdump failed, because of an error")
		print(str(e))
		if hasattr(e, "message"):
			print(e.message)
		traceback.print_exc(file=sys.stdout)
	finally:
		cleanup(1)


def beginthreads():
	gv.threads = []

	print("Starting %s offline check subprocesses..." % gv.offlineCheckThreads)
	for t in range(gv.offlineCheckThreads):
		bg = multiprocessing.Process(target=backgroundProcessWorker,
		                             args=(gv.offlineQueue, gv.dbQ, gv.CheckInQueue, gv.threadTerminationFlag))
		gv.threads.append(bg)
		bg.start()
	print("Starting %s worker subprocesses..." % gv.bg_worker_threads)
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
	if gv.loud:
		print("Getting equipment")
	for equipmentID, ip, name, model_id, subequipment in retrivalList(_id):
		# print equipmentID, ip, name
		query = "SELECT `id` from `status` WHERE `status`.`id` ='%d'" % equipmentID
		if len(gv.sql.qselect(query)) == 0:
			query = "REPLACE INTO `UMD`.`status` SET `id` ='%d'" % equipmentID
		gv.sql.qselect(query)
		for key in list(simpleTypes.keys()):

			if any(((key in model_id), (key in name))):
				newird = simpleTypes[key](int(equipmentID), ip, name, subequipment)
				break
		# elif "NS2000" in name: #Method not supported yet
		#	newird = equipment_new.NS2000(int(equipmentID), ip, name)
		else:
			newird = equipment.generic.GenericIRD(int(equipmentID), ip, name, subequipment)
		gv.addEquipment(newird)
	# print gv.equipmentDict
	if gv.loud:
		print("Determining types")
	for currentEquipment in list(gv.equipmentDict.values()):
		gv.ThreadCommandQueue.put(("determine_type", currentEquipment.serialize()), block=True)


def dbworker(myQ):
	import time
	item = 1

	gotdata = True
	while gv.threadTerminationFlag.value == False:
		# while not gv.ThreadCommandQueue.empty():
		# print "still in while"
		# func, data = gv.ThreadCommandQueue.get()
		try:
			cmd = myQ.get(timeout=1)
			gotdata = True

		except queue.Empty:
			time.sleep(0.1)
			gotdata = False

		if gotdata:
			# print  "Processing Item %s" % item
			gv.sql.qselect(cmd)
			myQ.task_done()


# thread.exit()
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
						if instance.checkout.getStatus() in [STAT_INIT, STAT_READY, STAT_STUCK]:
							if isinstance(instance, server.equipment.generic.GenericIRD):
								task = "determine_type"
								myq = gv.ThreadCommandQueue
							else:
								if instance.get_offline():
									task = "determine_type"
									myq = gv.offlineQueue
								else:
									task = "refresh"
									myq = gv.ThreadCommandQueue
							myq.put((task, gv.equipmentDict[equipmentID].serialize()))
							instance.checkout.enqueue()
					except queue.Full:
						time.sleep(0.1)
						continue
			else:
				time.sleep(0.1)


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
					print("checkin fail")
					print(data)
				del data
			except queue.Empty:
				gv.gotCheckedInData = False
				time.sleep(0.1)


def backgroundProcessWorker(myQ, dbQ, checkInQueue, endFlag):
	""" Entry point for sub process """
	from . import gv
	from helpers import mysql
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
	item = 1

	def getTerminated():
		try:
			return endFlag.value
		except (AttributeError, OSError):  # This fails in the profiler
			return gv.threadTerminationFlag.value

	gotdata = True
	while not getTerminated():
		# while not gv.ThreadCommandQueue.empty():
		# print "still in while"
		# func, data = gv.ThreadCommandQueue.get()

		try:
			func, data = myQ.get(timeout=1)
			gotdata = True

		except queue.Empty:
			time.sleep(0.1)
			gotdata = False

		if gotdata:
			# print  "Processing Item %s" % item
			error = None
			try:
				bgtask.funcs[func](data)
			except KeyboardInterrupt:
				print("processs %s caught KeyboardInterrupt and is closing" % multiprocessing.current_process())
				return

			except Exception as e:
				try:
					message = e.message
				except AttributeError:
					message = "no message"

				sys.stderr.write("Error in processs %s ignored. error type is %s and message is %s\n" % (
				multiprocessing.current_process(), e, message))
				traceback.print_exc(file=sys.stdout)
				sys.stderr.flush()

			finally:
				# print "processed a thred command!s"
				myQ.task_done()

			# if error:
			# gv.exceptions.append(( error[1], traceback.format_tb(error[2]) ))
			item += 1


import atexit


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
			print("Set termination flag")
			time.sleep(1)
			print("Joining threads and waiting for subprocesses")
			for thread in gv.threads:
				thread.join(1)
				print(".", end=' ')
			if exit_status == 0:
				cmd = "UPDATE `UMD`.`management` SET `value` = 'OFFLINE' WHERE `management`.`key` = 'current_status';"
				gv.sql.qselect(cmd)

			gv.sql.close()
			gv.preexit = True
		except Exception as e:
			print("%s error during shutdown" % type(e))
			exit_status = 1
		finally:
			sys.exit(exit_status)


def main(debugBreak=False):
	print("Started at " + time.strftime("%H:%M:%S"))
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
	print("Types determined. Took %s seconds. Begininng main loop. Press CTRL C to %s" % (
	time.time() - time1, ["quit", "enter debug console"][gv.debug]))
	if gv.debug:


		all_objects = muppy.get_objects()
		gv.mem_sum1 = summary.summarize(all_objects)

	print("Starting dispatch")
	gv.threads[gv.dispatcherThread].start()

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
	while gv.threadTerminationFlag.value == False:
		try:

			if not finishedStarting:
				cmd = "UPDATE `UMD`.`management` SET `value` = 'RUNNING' WHERE `management`.`key` = 'current_status';"
				gv.dbQ.put(cmd)
			finishedStarting = True

			loopcounter += 1
			if loopcounter > 10:  # Restart all threads every 10 minutes
				loopcounter = 0
				if gv.loud:
					print("Stopping dispatcher")
				gv.threadJoinFlag = True
				gv.ThreadCommandQueue.join()
				if gv.loud:
					print("Garbage Collection")
				collected = gc.collect()
				if gv.loud:
					print("collected %s objects. Resuming" % collected)
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
							if gv.loud:
								print("%s: %s" % (equipmentID, jitter))
							"""
							if float(jitter) > 30:
								gv.equipmentDict[equipmentID].set_offline()
								offcount += 1
							else:
								oncount += 1
							"""


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
					print("Refresh statistics loop %s" % loopcounter)
					print("Minimum refresh time %s seconds" % gv.min_refresh_time)
					print("MAX: %s MIN: %s AVG:%s " % (
					max(jitterlist) + gv.min_refresh_time, min(jitterlist) + gv.min_refresh_time,
					avg(jitterlist) + gv.min_refresh_time))
					print("%s stopped threads. %s running threads" % (stoppedThreads, runningThreads))
					for k, v in tallyDict.items():
						print("%d in status %s" % (v, k))
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
					print("Min refresh time now %s" % gv.min_refresh_time)
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
					print("Leaving loop")
					return

				"""
				for thread in gv.threads:
					thread.run()
				"""

			time.sleep(30)
		except KeyboardInterrupt:
			if gv.debug:
				gv.threadJoinFlag = True
				print("Pausing to debug")
				debug.debug_breakpoint()
			else:
				print("Quitting")
				cleanup()
				break
		except AssertionError as e:
			if gv.debug:
				gv.threadJoinFlag = True
				print("Pausing to debug because of %s" % e.message)
				debug.debug_breakpoint()
			else:
				print("Program Self Check has caused program to quit.")
				print("")
				print("%s Error." % str(e))

				print("Offline Equipment:")
				for equipmentID in list(gv.equipmentDict.keys()):
					try:
						if gv.equipmentDict[equipmentID].get_offline():
							eq = gv.equipmentDict[equipmentID]
							print(eq.name.ljust(10, " ") + eq.modelType.ljust(10, " ") + eq.ip)
					except:
						continue
				print("errors:")
				print(gv.exceptions)
				crashdump()
		except Exception as e:
			print("Other error of type %s" % type(e))
			gv.exceptions.append((e, traceback.format_tb(sys.exc_info()[2])))
			try:
				message = e.message
			except:
				message = ""
			print("%s: %s." % (e, message))
			if gv.debug:
				gv.threadJoinFlag = True
				print("Pausing to debug")
				debug.debug_breakpoint()
			else:
				crashdump()
