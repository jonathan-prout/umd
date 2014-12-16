#!/usr/bin/python
import os, re, string,threading
import sys,time,datetime

import socket
import getopt
import time

from helpers import mysql
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

def main(loop):
	#global gv.sql
	now = datetime.datetime.now()
	umdServerRunning = False
	
	
	global streamcodes
	res = ""
	
	gv.mv = {}
	global threads
	threads = []
	
	cmd = "SELECT `id`,`Name`,`IP`,`Protocol` FROM `Multiviewer` "
	d = {"id":0,"Name":1,"IP":2,"Protocol":3}
	res = gv.sql.qselect(cmd)
	threadcounter = 0
	
	# Get multiviewers
	for line in res:
		mul = getMultiviewer(line[ d["Protocol"]], line[ d["IP"]]) # returns mv instance
		gv.mvID[ line[ d["IP"]]] =  line[ d["id"]]
		mul.lookuptable = getAddresses(line[ d["IP"]]) #multiviewer input table
		gv.mv[line[ d["IP"]]] = mul 
		bg = myThread(threadcounter, line[d["Name"]], threadcounter, gv.mv[line[ d["IP"]]]) #put multivier in thread
		bg.daemon = True
		mythreads.append(bg)
		bg.start()
		threadcounter += 1
		
	
	
	print "Now starting main loop press ctrl c to quit"
	gv.display_server_status = "Running"
	writeCustom()
	writeDefaults()
	while 1:
		#print "Iteration %s"% counter
		try:
			for x in range(60):
				cmd = 'SELECT `value` FROM `management` where `key` = "current_status";'
				pollstatus = gv.sql.qselect(cmd)[0][0]
				if pollstatus == "RUNNING":
					umdServerRunning = True
					getrxes()
					writeCustom()
				else:
					if umdServerRunning == True:
						mv[m].fullref = True
						umdServerRunning = False
					
					writeStatus("Display: %s, Polling: %s"%(gv.display_server_status, pollstatus))
				
				time.sleep(1)
				if not loop:
					return
				
			for m in mv.keys():
				
				mv[m].fullref = True
				
				"""
				if mv[m].get_offline():
					try:
						logwrite("%s is offline"%m)
						mv[m].connect()
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
			"TOP": "0" + str(i),
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
	
	return gv.sql.qselect(request), commands, cmap
	


def getCustom():
	commands = ["kaleidoaddr",  "input",  "top",  "bottom",  "address1",  "address2"]
	cmap = {}
	for x in range(len(commands)):
		cmap[commands[x]] = x
		request = "SELECT "
	request += ",".join(commands)
	request += "  FROM `customlabel`  "
	return gv.sql.qselect(request), commands, cmap
def writeCustom():
	res, commands, cmap = getCustom()
	for i in range(0,len(res)):
			
			j = {}
			
			for k in commands:
				j[k] = res[i][cmap[k]]
			
			if j["kaleidoaddr"] in mv.keys():
				if "sameas=" in j["top"]:
					try:
						s, eid = j["top"].split("=")
						mv[j["kaleidoaddr"]].put( ( int(j["input"]) , "TOP", gv.labelcache[int(eid)]["TOP"], "TEXT")   )
						mv[j["kaleidoaddr"]].put( ( int(j["input"]) , "BOTTOM", gv.labelcache[int(eid)]["BOTTOM"], "TEXT")   )
					except Exception as e:
						mv[j["kaleidoaddr"]].put( ( int(j["input"]) , "TOP", str(eid), "TEXT")   )
						errortext =  e.__repr__()
						errortext = errortext.replace("(", " ")
						errortext = errortext.replace(")", " ")
						mv[j["kaleidoaddr"]].put( ( int(j["input"]) , "BOTTOM", "%s"% errortext, "TEXT")   )
				else:
					mv[j["kaleidoaddr"]].put( ( int(j["input"]) , "TOP", j["top"], "TEXT")   )
					mv[j["kaleidoaddr"]].put(  ( int(j["input"]) , "BOTTOM", j["bottom"], "TEXT") )   	
	
def writeStatus(status):
	""" Write Errors to the multiviewer """
	for addr in mv.keys():
		klist = sorted(mv[addr].lookuptable.keys())
		for key in range(0, len(klist), 16):
			try: 
				mv[addr].put( (klist[key], "BOTTOM", status, multiviewer.generic.status_message.textMode) )
			except:
				pass
		

inputStrategies = enum("Reserved", "equip", "matrix", "indirect", "label")
def getStatusMesage(mvInput, mvHost):
	
	happyStatuses = ["RUNNING"]
	pollstatus = getPollStatus()
	displayStatus = gv.display_server_status
	
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
	if all((pollstatus in happyStatuses, displayStatus in happyStatuses)):
		if all((res["strategy"] == inputStrategies.equip, res["equipment"] not in [None, 0])):
				sm = gv.equip[res["equipment"]].getStatusMessage()
		elif res["strategy"] == inputStrategies.matrix:
			mtxIn = mtxLookup[res["inputmtxname"]]
			if gv.getEquipByName(mtxIn):
				sm = gv.equip[gv.getEquipByName()].getStatusMessage()
			else:
				sm = labelmodel.matrixResult(mtxIn).getStatusMessage()
		elif res["strategy"] == inputStrategies.indirect:
			sm = labelmodel.matrixResult(res["inputmtxname"]).getStatusMessage()
		elif res["strategy"] == inputStrategies.label:
			if res["customlabel1"]:
				sm.topLabel = res["customlabel1"]
			if res["customlabel2"]:
				sm.bottomLabel = res["customlabel2"]
	else:
		if all((res["strategy"] == inputStrategies.equip, res["equipment"] not in [None, 0])):
				sm.topLabel = gv.equip[res["equipment"]].isCalled()
		elif res["strategy"] == inputStrategies.label:
			if res["customlabel1"]:
				sm.topLabel = res["customlabel1"]
			if res["customlabel2"]:
				sm.bottomLabel = res["customlabel2"]
		else:
			sm.topLabel = res["inputmtxname"]
	
	
		if mvInput %16 == 1:
			sm.bottomLabel = "Display: %s, Polling:%s"%(displayStatus, pollstatus)


		
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
class matrixThread(mvThread):
	def run(self):
		matrixrefresh(self.instance, self.name)
		
def matrixrefresh(myInstance, name):            
	while not gv.threadTerminationFlag:
		myInstance.refresh()
		time.sleep(1)

def mvrefresh(myInstance, name):            
	while not gv.threadTerminationFlag:
		
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
				myInstance.put(getStatusMessage(i, myInstance.host))
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
		writeDefaults()
		writeStatus("Display: %s, Polling: %s"%(gv.display_server_status, pollstatus))
		running = False
		gv.threadTerminationFlag = True
		for t in mythreads:
			t.join(10)
		



		

		
