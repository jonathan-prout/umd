#!/usr/bin/python
from __future__ import print_function
from __future__ import absolute_import
import threading
import datetime

import time

import MySQLdb

import client
import client.multiviewer.miranda
import client.multiviewer.harris
import client.multiviewer.gvgmv

import client.status
from helpers import alarm, virtualmatrix
from client import multiviewer
from client import gv
from client import labelmodel
from helpers.logging import log

gv.display_server_status = "Starting"
ASI_MODE_TEXT = "ASI"
remove_hz = True
ebno_alarm_base = 500
rec_alarm_base = 600

mythreads = []
logfile = "/var/www/programming/client/client_error.txt"
loud = False
errors_in_stdout = False

def logwrite(errortext): # TODO I don't like this so will refactor with python logging
	if any((loud, errors_in_stdout)):
		print("**** ERROR!! ******")
		print("\n".join(errortext))
		print("***********************")
	file = open(logfile, "a")
	errortext.append(" ")
	file.write("\n".join(errortext))
	file.close()


streamcodes = []


def bitrateToStreamcode(muxbitrate):
	tolerance = float(0.125)
	# streamcodes == []:
	streamcodes = gv.sql.qselect("SELECT `name`, `bitrate` FROM `streamcodes` WHERE 1")

	try:
		bitratefloat = float(muxbitrate)
		bitratefloat = (bitratefloat / 1000000)  # bps to mbps
	except:
		bitratefloat = 0

	for name, streamBitrate in streamcodes:
		streamBitratee = float(streamBitrate)
		if (streamBitrate - tolerance < bitratefloat < streamBitrate + tolerance):
			bitratestring = name
			break
		else:
			bitratestring = str(bitratefloat)[:4]
	return bitratestring


def main(loop, test=None):
	""" Main thread's main function started after runsserver starts
	"""

	now = datetime.datetime.now()
	umdServerRunning = False

	global streamcodes
	res = ""

	# Store multiviewers here
	gv.mv = {}

	# Store threads here
	gv.threads = []

	# Make a dict and put matrixes that do different things into the different dicts
	matrixCapabilites = ["SDI", "ASI", "LBAND", "IP"]
	for k in matrixCapabilites:
		gv.matrixCapabilities[k] = []

	# Use matrix db to get the matrix names
	gv.sql.qselect("use matrix")
	matrixNames = gv.sql.qselect("select mtxName from matrixes")[0]

	# Go back to the UMD database
	gv.sql.qselect("use UMD")

	# Create a virtual matrix for each matrix and include it in each capabitlity
	for m in matrixNames:
		mtx = virtualmatrix.virtualMatrix(m)
		gv.matrixes.append(mtx)
		for k in matrixCapabilites:
			if k in mtx.prefsDict["capabilitiy"]:
				gv.matrixCapabilities[k].append(mtx)

	# Start threads
	threadcounter = 0
	bg = dbThread(threadcounter, "database thread", threadcounter, None)
	bg.daemon = True
	gv.threads.append(bg)
	bg.start()
	threadcounter += 1
	cmd = "SELECT `id`,`Name`,`IP`,`Protocol` FROM `Multiviewer` "
	d = {"id": 0, "Name": 1, "IP": 2, "Protocol": 3}
	res = gv.sql.qselect(cmd)

	# Test mode is to test the labeling system
	if test:
		for line in res:
			if line[d["IP"]] == test:
				break
		else:
			print("'%s' not in the multiviewer table" % test)
			return

		mul = multiviewer.generic.TestMultiviewer(line[d["IP"]])
		gv.mvID[line[d["IP"]]] = line[d["id"]]
		print(getAddresses(line[d["IP"]]))
		mul.lookuptable = getAddresses(line[d["IP"]])
		print("Started test")
		while 1:
			try:
				for i in list(mul.lookuptable.keys()):
					for x in mul.get_status_message(i, mul.id).__iter__():
						print(x)
					mul.put(mul.get_status_message(i, mul.id))
				mul.refresh()
				time.sleep(1)
				gv.display_server_status = "Running"

			except KeyboardInterrupt:
				return
	else:

		for line in res:
			mul = getMultiviewer(line[d["Protocol"]], line[d["IP"]], line[d["id"]], line[d["Name"]])  # returns mv instance
			gv.mvID[line[d["IP"]]] = line[d["id"]]  # Store the id in a dict
			mul.lookuptable = getAddresses(line[d["IP"]])  # multiviewer IP dicr
			gv.mv[line[d["IP"]]] = mul  # mulitviewer storage by IP
			# put multivier in thread
			bg = mvThread(threadcounter, line[d["Name"]], threadcounter,
							gv.mv[line[d["IP"]]])
			bg.daemon = True
			gv.threads.append(bg)
			bg.start()
			threadcounter += 1

	print("Now starting main loop press ctrl c to quit")
	gv.display_server_status = "Running"

	# Main thread will sleep unil keyboard interrupt.
	while 1:
		try:
			for x in range(60):
				time.sleep(1)
				if not loop:
					return

			for m in list(gv.mv.keys()):
				gv.mv[m].fullref = True

		except KeyboardInterrupt:
			print("You pressed control c, so I am quitting")
			return
	# Runclient will call shutdown now


def getAddresses(ip):
	cmd = "SELECT `input`, `labeladdr1`, `labeladdr2` FROM `mv_input` WHERE `multiviewer` =%d" % gv.mvID[ip]
	res = gv.sql.qselect(cmd)
	lookuptable = {}
	for line in res:
		i, labeladdr1, labeladdr2 = line
		i = int(i)
		d = {
			"TOP": i,
			"BOTTOM": 100 + i,
			"C/N": 500 + i,
			"REC": 600 + i,
			"COMBINED": 200 + i
		}
		if labeladdr1:
			d["TOP"] = int(labeladdr1)
		if labeladdr2:
			d["BOTTOM"] = int(labeladdr2)
		lookuptable[i] = d
	return lookuptable


def getdb():
	with gv.equipDBLock:


		colourd = {}
		colours = gv.sql.qselect('SELECT name, colour FROM UMD.colours;')
		try:
			gv.sql.db.commit()  #Wasn't updating without commit
		except MySQLdb.ProgrammingError:
			log("Resetting db", "update thread", alarm.level.Info)
			gv.sql.db.close()
			gv.sql.connect()
		for name, colour in colours:
			colourd[name] = colour
		gv.colours = colourd
		request = "SELECT "
		commands = labelmodel.irdResult.commands

		cmap = {}
		for x in range(len(commands)):
			cmap[commands[x]] = x
		request += ",".join(commands)
		request += " FROM equipment e, status s WHERE e.id = s.id "

		gv.equip = {}
		for item in gv.sql.qselect(request):
			equipmentID = int(item[cmap["e.id"]])
			gv.equip[equipmentID] = labelmodel.irdResult(equipmentID, item)

		for matrix in gv.matrixes:
			matrix.refresh()


def writeStatus(status):
	""" Write Errors to the multiviewer """
	for addr in gv.mv.keys():
		klist = sorted(gv.mv[addr].lookuptable.keys())
		for key in range(0, len(klist), 16):
			try:
				gv.mv[addr].put((klist[key], "BOTTOM", status, client.status.status_message.textMode))
			except queue.Full:
				pass


def getMultiviewer(mvType, host, mvID, name):
	gv.sql.qselect('UPDATE `Multiviewer` SET `status` = "STARTING" WHERE `id` = "%s";' % mvID)
	if mvType in ["kaleido", "Kaleido"]:
		print("Starting Kaleido")
		mv = client.multiviewer.miranda.kaleido(host, mvID, name)
		return mv
	elif mvType in ["k2", "K2"]:
		print("Starting K2 {} {}".format(name, host))
		return client.multiviewer.miranda.K2(host, mvID, name)
	elif mvType in ["KX", "KX"]:
		print("Starting KX {} {}".format(name, host))
		return client.multiviewer.miranda.KX(host, mvID, name)
	elif mvType in ["KX16", "KX-16"]:
		print("Starting KX-16 {} {}".format(name, host) )
		return client.multiviewer.miranda.KX16(host, mvID, name)
	elif mvType in ["KXQUAD", "KX-QUAD {} {}".format(name, host)]:
		print("Starting KX-QUAD")
		return client.multiviewer.miranda.KXQUAD(host, mvID, name)
	elif mvType in ["GVMultiviewer", "GV-Multiviewer", "GVMultiv"]:
		print("Starting GV-Multiviewer {} {}".format(name, host))
		return client.multiviewer.gvgmv.GvMv(host,  mvID, name)
	else:  # Harris/Zandar
		print("Starting Harris {} {}".format(name, host))
		return client.multiviewer.harris.zprotocol(host,  mvID, name)


class mvThread(threading.Thread):
	""" Thread for holding the multiviewer """
	def __init__(self, threadID, name, counter, instance):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
		self.instance = instance

	def run(self):
		""" Runs the mvrefresh function"""
		self.instance.start()
		mvrefresh(self.instance, self.name)



def dbrefresh():
	while not gv.threadTerminationFlag:
		getdb()
		time.sleep(1)


class dbThread(mvThread):
	def run(self):
		dbrefresh()


def mvrefresh(myInstance, name):
	""" Function for multivewer updates """
	while not gv.threadTerminationFlag:
		# If it's offline, wait 60s before reconnection attempts
		if myInstance.get_offline():
			gv.sql.qselect('UPDATE `Multiviewer` SET `status` = "OFFLINE" WHERE `id` = "%s";' % myInstance.id)
			for seconds in range(60):
				if gv.programTerminationFlag:
					return
				time.sleep(1)
			if gv.loud:
				print("Attempting to reconnect to %s" % name)
				myInstance.connect()
		# If it's online
		if not myInstance.get_offline():
			gv.sql.qselect('UPDATE `Multiviewer` SET `status` = "OK" WHERE `id` = "%s";' % myInstance.id)

			# Generate a status message for each multiviwer input
			for i in myInstance.lookuptable.keys():
				myInstance.put(myInstance.get_status_message(i, myInstance.id))
			# Now call the refresh function and loop
			# Refresh reads through all the status messages and writes to the multiviewer
			myInstance.refresh()
			time.sleep(1)
	print("Stopping display for %s" % name)
	gv.sql.qselect('UPDATE `Multiviewer` SET `status` = "OFFLINE" WHERE `id` = "%s";' % myInstance.id)


# print "Leaving thread as termintation flag set"

def shutdown(exit_status):
	gv.programTerminationFlag = True
	cmd = 'SELECT `value` FROM `management` where `key` = "current_status";'
	pollstatus = gv.sql.qselect(cmd)[0][0]
	if exit_status == 0:
		gv.display_server_status = "OFFLINE"
	else:
		gv.display_server_status = "OFFLINE_ERROR"
	# writeDefaults()
	writeStatus("Display: %s, Polling: %s" % (gv.display_server_status, pollstatus))
	running = False
	gv.threadTerminationFlag = True
	for t in mythreads:
		t.join(10)
