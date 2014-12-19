#!/usr/bin/python
import os, re, string,threading
import sys,time,datetime

import socket
import getopt
import time

from helpers import mysql
from helpers import virtualmatrix
import multiviewer
import gv
import labelmodel


gv.display_server_status = "Starting"
ASI_MODE_TEXT = "ASI"
remove_hz = True
ebno_alarm_base = 500
rec_alarm_base = 600

mythreads = []
logfile = "/var/www/programming/client/client_error.txt"
loud = False
errors_in_stdout = False



def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

		
		
def logwrite(errortext):
	if any((loud, errors_in_stdout)):
			print "**** ERROR!! ******"
			print "\n".join(errortext)
			print "***********************"
	file = open(logfile,"a")
	errortext.append(" ")
	file.write("\n".join(errortext))
	file.close()	

streamcodes = []






def bitrateToStreamcode(muxbitrate):
	tolerance = float(0.125)
	#streamcodes == []:
	streamcodes = gv.sql.qselect("SELECT `name`, `bitrate` FROM `streamcodes` WHERE 1")
	
	
	try:
		bitratefloat = float(muxbitrate)
		bitratefloat = (bitratefloat / 1000000) #bps to mbps
	except:
		bitratefloat = 0
	
	
	for name, streamBitrate in streamcodes:
		streamBitratee = float(streamBitrate)
		if(streamBitrate - tolerance  < bitratefloat <streamBitrate + tolerance):
			bitratestring = name
			break
		else:
			bitratestring = str(bitratefloat)[:4]
	return bitratestring	
	
def getPollStatus():
	cmd = 'SELECT `value` FROM `management` where `key` = "current_status";'
	pollstatus = gv.sql.qselect(cmd)[0][0]
	return pollstatus

def main(loop, test = None):
	#global gv.sql
	now = datetime.datetime.now()
	umdServerRunning = False
	
	
	global streamcodes
	res = ""
	
	gv.mv = {}
	global threads
	threads = []
	
	matrixCapabilites = ["SDI", "ASI", "LBAND", "IP"]
	for k in matrixCapabilites:
		gv.matrixCapabilities[k] = []
	matrixNames = ["UMDASC1","lband"]
	for m in matrixNames:
		mtx = virtualmatrix.virtualMatrix(m)
		gv.matrixes.append(mtx)
		for k in matrixCapabilites:
			if k in mtx.prefsDict["capabilitiy"]:
				gv.matrixCapabilities[k].append(mtx)
	
	threadcounter = 0
	bg = dbThread(threadcounter, "database thread", threadcounter, None)
	bg.daemon = True
	gv.threads.append(bg)
	bg.start()
	threadcounter += 1
	cmd = "SELECT `id`,`Name`,`IP`,`Protocol` FROM `Multiviewer` "
	d = {"id":0,"Name":1,"IP":2,"Protocol":3}
	res = gv.sql.qselect(cmd)
	if test:
		mul = multiviewer.generic.testmultiviewer(test)
		
		for line in res:
			if line[ d["IP"]] == test:
					break
		else:
			print "'%s' not in the multiviewer table"%test
			return
		mul = multiviewer.generic.testmultiviewer(line[ d["IP"]])
		gv.mvID[ line[ d["IP"]]] =  line[ d["id"]]
		print  getAddresses(line[ d["IP"]])
		mul.lookuptable = getAddresses(line[ d["IP"]])
		"""
		gv.mv[line[ d["IP"]]] = mul 
		bg = mvThread(threadcounter, line[d["Name"]], threadcounter, gv.mv[line[ d["IP"]]]) #put multivier in thread
		bg.daemon = True
		gv.threads.append(bg)
		bg.start()
		threadcounter += 1
		"""
		print "Started test"
		while 1:
			try:
				for i in mul.lookuptable.keys():
					for x in getStatusMesage(i, mul.host).__iter__(): print x
					mul.put(getStatusMesage(i, mul.host))
				mul.refresh()
				time.sleep(1)
				gv.display_server_status = "Running"

			except KeyboardInterrupt:
				return
	else:

		for line in res:
			mul = getMultiviewer(line[ d["Protocol"]], line[ d["IP"]]) # returns mv instance
			gv.mvID[ line[ d["IP"]]] =  line[ d["id"]]
			mul.lookuptable = getAddresses(line[ d["IP"]]) #multiviewer input table
			gv.mv[line[ d["IP"]]] = mul 
			bg = mvThread(threadcounter, line[d["Name"]], threadcounter, gv.mv[line[ d["IP"]]]) #put multivier in thread
			bg.daemon = True
			gv.threads.append(bg)
			bg.start()
			threadcounter += 1
		
	print "Now starting main loop press ctrl c to quit"
	gv.display_server_status = "Running"
	
	
	while 1:
		#print "Iteration %s"% counter
		try:
			for x in range(60):
				"""
				cmd = 'SELECT `value` FROM `management` where `key` = "current_status";'
				pollstatus = gv.sql.qselect(cmd)[0][0]
				if pollstatus == "RUNNING":
					umdServerRunning = True
					getrxes()
					writeCustom()
				else:
					if umdServerRunning == True:
						gv.mv[m].fullref = True
						umdServerRunning = False
					
					writeStatus("Display: %s, Polling: %s"%(gv.display_server_status, pollstatus))
				"""
				time.sleep(1)
				if not loop:
					return
				
			for m in gv.mv.keys():
				
				gv.mv[m].fullref = True
				
				"""
				if gv.mv[m].get_offline():
					try:
						logwrite("%s is offline"%m)
						gv.mv[m].connect()
					except: pass
				"""
		except KeyboardInterrupt:
			print "You pressed control c, so I am quitting"
			return
	
def getAddresses(ip):
	cmd = "SELECT `input`, `labeladdr1`, `labeladdr2` FROM `mv_input` WHERE `multiviewer` =%d"%gv.mvID[ip]
	res = gv.sql.qselect(cmd)
	lookuptable = {}
	for line in res:
		i, labeladdr1, labeladdr2 = line
		i = int(i)
		d = {
			"TOP": i,
			"BOTTOM": 100 + i,
			"C/N": 500 + i,
			"REC": 600 + i
		}
		if labeladdr1:
			d["TOP"] = int(labeladdr1)
		if labeladdr2:
			d["BOTTOM"] = int(labeladdr2)
		lookuptable[i] = d
	return lookuptable

			

def getdb():
	#	request = "SELECT s.servicename,s.aspectratio,s.ebno,s.pol,s.castatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,e.labelnamestatic,s.framerate FROM equipment e, status s WHERE e.id = s.id"
	with gv.equipDBLock:
		
	
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
				gv.mv[addr].put( (klist[key], "BOTTOM", status, multiviewer.generic.status_message.textMode) )
			except:
				pass
		

inputStrategies = enum("Reserved", "equip", "matrix", "indirect", "label")
def getStatusMesage(mvInput, mvHost):
	with gv.equipDBLock:
		
		happyStatuses = ["RUNNING"]
		pollstatus = getPollStatus().upper()
		displayStatus = gv.display_server_status.upper()
		
		sm = multiviewer.generic.status_message()
		fields = ["strategy", "equipment", "inputmtxid", "inputmtxname", "customlabel1", "customlabel2"]
		fn = []
		cmap = {}
		i = 0
		for f in fields:
			fn.append("`mv_input`.`%s`"%f)
			cmap[f] = i
			i += 1
		
		cmd = "SELECT "
		cmd += " , ".join(fn)
		cmd += "FROM `mv_input`"
		cmd += "WHERE ((`mv_input`.`multiviewer` =%d) AND (`mv_input`.`input` =%d))"%(gv.mvID[mvHost],mvInput)
		
		res = dict(zip(fields, gv.sql.qselect(cmd)[0]))
		#print cmd
		#print res
		if all((pollstatus in happyStatuses, displayStatus in happyStatuses)):
			try:
								if gv.equip[int(res["equipment"])] is not None:
									tlOK = True
								else:
									tlOK = False
								e = None
			except Exception, e:
					tlOK = False
					if all((int(res["strategy"]) == int(inputStrategies.equip), tlOK )):
						sm = gv.equip[res["equipment"]].getStatusMessage()
						assert sm is not None
					elif res["strategy"] == inputStrategies.matrix:
						mtxIn = gv.mtxLookup(res["inputmtxname"])
						if gv.getEquipByName(mtxIn):
							sm = gv.equip[gv.getEquipByName(mtxIn)].getStatusMessage()
							assert sm is not None
						else:
							sm = labelmodel.matrixResult(mtxIn).getStatusMessage()
							assert sm is not None
					elif res["strategy"] == inputStrategies.indirect:
						sm = labelmodel.matrixResult(res["inputmtxname"]).getStatusMessage()
						assert sm is not None
					elif res["strategy"] == inputStrategies.label:
						if res["customlabel1"]:
							sm.topLabel = res["customlabel1"]
						if res["customlabel2"]:
							sm.bottomLabel = res["customlabel2"]
		else:
			try: 
				if gv.equip[int(res["equipment"])] is not None:
					tlOK = True
				else:
					tlOK = False
				e = None
			except Exception, e:
				tlOK = False
			if all((int(res["strategy"]) == int(inputStrategies.equip), tlOK )):
					sm.topLabel = gv.equip[int(res["equipment"])].isCalled()
					sm.bottomLabel = " "
			elif res["strategy"] == inputStrategies.label:
				if res["customlabel1"]:
					sm.topLabel = res["customlabel1"]
				if res["customlabel2"]:
					sm.bottomLabel = res["customlabel2"]
			else:
				sm.topLabel = res["inputmtxname"]
				#sm.bottomLabel = "%s, %s %s,%s"%(res["equipment"],len(gv.equip.keys()),e, int(res["strategy"]) )
				sm.bottomLabel = " "
			if mvInput %16 == 1:
				sm.bottomLabel = "Display: %s, Polling:%s"%(displayStatus, pollstatus)
		
			
		sm.mv_input = mvInput
	
	return sm
		
def getMultiviewer(mvType, host):
	gv.sql.qselect('UPDATE `Multiviewer` SET `status` = "STARTING" WHERE `IP` = "%s";'%host)
	if mvType in ["kaleido", "Kaleido"]:
	    print "Starting Kaleido"
	    return multiviewer.miranda.kaleido(host)
	elif mvType in ["k2", "K2"]:
	    print "Starting K2"
	    return multiviewer.miranda.K2(host)
	elif mvType in ["KX", "KX"]:
	    print "Starting KX"
	    return multiviewer.miranda.KX(host)
	elif mvType in ["KX16", "KX-16"]:
	    print "Starting KX-16"
	    return multiviewer.miranda.KX16(host)
	elif mvType in ["KXQUAD", "KX-QUAD"]:
	    print "Starting KX-QUAD"
	    return multiviewer.miranda.KXQUAD(host)
	else: #Harris/Zandar
	    print "Starting Harris" 
	    return multiviewer.harris.zprotocol(host)



class mvThread (threading.Thread):
    def __init__(self, threadID, name, counter, instance):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.instance = instance
    def run(self):
        #print "Starting " + self.name
        mvrefresh(self.instance, self.name)
        #print "Exiting " + self.name


def dbrefresh():
        while not gv.threadTerminationFlag:
                getdb()
                time.sleep(1)




class dbThread(mvThread):
	def run(self):
		dbrefresh()


def mvrefresh(myInstance, name):            
	
	while not gv.threadTerminationFlag:
		print "mvrefr"
		if myInstance.get_offline():
			
			gv.sql.qselect('UPDATE `Multiviewer` SET `status` = "OFFLINE" WHERE `IP` = "%s";'%myInstance.host)
		
			for seconds in range(60):
				if gv.programTerminationFlag:
					return
				time.sleep(1) # wait between connection attempts
				
			if gv.loud:
				print "Attempting to reconnect to %s"% name
				myInstance.connect()
			

		
			
		if not myInstance.get_offline():
			gv.sql.qselect('UPDATE `Multiviewer` SET `status` = "OK" WHERE `IP` = "%s";'%myInstance.host)
			for i in myInstance.lookuptable.keys():
				myInstance.put(getStatusMesage(i, myInstance.host))
			myInstance.refresh()
			time.sleep(1)
	print "Stopping display for %s"% name
	gv.sql.qselect('UPDATE `Multiviewer` SET `status` = "OFFLINE" WHERE `IP` = "%s";'%myInstance.host)
	#print "Leaving thread as termintation flag set"

def shutdown(exit_status):
		import sys
		gv.programTerminationFlag = True
		cmd = 'SELECT `value` FROM `management` where `key` = "current_status";'
		pollstatus = gv.sql.qselect(cmd)[0][0]
		if exit_status == 0:
			gv.display_server_status = "OFFLINE"
		else:
			gv.display_server_status = "OFFLINE_ERROR"
		#writeDefaults()
		writeStatus("Display: %s, Polling: %s"%(gv.display_server_status, pollstatus))
		running = False
		gv.threadTerminationFlag = True
		for t in mythreads:
			t.join(10)
		



		

		
