#!/usr/bin/python
import os, re, string,threading
import sys,time,datetime

import socket
import getopt
import time

from helpers import mysql
import multiviewer
import gv

gv.display_server_status = "Starting"
ASI_MODE_TEXT = "ASI"
remove_hz = True
ebno_alarm_base = 500
rec_alarm_base = 600

mythreads = []
logfile = "/var/www/programming/client/client_error.txt"
loud = False
errors_in_stdout = False





		
		
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
	
def main(loop):
	#global gv.sql
	now = datetime.datetime.now()
	umdServerRunning = False
	
	
	global streamcodes
	res = ""
	global mv
	mv = {}
	global threads
	threads = []
	
	cmd = "SELECT `id`,`Name`,`IP`,`Protocol` FROM `Multiviewer` "
	d = {"id":0,"Name":1,"IP":2,"Protocol":3}
	res = gv.sql.qselect(cmd)
	threadcounter = 0
	cmd = 'SELECT `value` FROM `management` where `key` = "current_status";'
	pollstatus = gv.sql.qselect(cmd)[0][0]
	# Get multiviewers
	for line in res:
		mul = getMultiviewer(line[ d["Protocol"]], line[ d["IP"]]) # returns mv instance
		
		mul.lookuptable = getAddresses(line[ d["IP"]]) #multiviewer input table
		mv[line[ d["IP"]]] = mul 
		bg = myThread(threadcounter, line[d["Name"]], threadcounter, mv[line[ d["IP"]]]) #put multivier in thread
		bg.daemon = True
		mythreads.append(bg)
		bg.start()
		threadcounter += 1
		writeStatus("Display: %s, Polling:%s"%(gv.display_server_status, pollstatus))
	writeDefaults()
	
	
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
	res, commands, cmap = getdb()
	addresses = {}
	for i in range(0,len(res)):
			
			j = {}
			
			for k in commands:
				j[k] = res[i][cmap[k]]
			
	
			if j["e.kaleidoaddr"] == ip:
				
				d = {
				"TOP": int(j["e.labeladdr"]),
				"BOTTOM": int(j["e.labeladdr2"]),
				"C/N": 500 + int(j["e.kid"]),
				"REC": 600 + int(j["e.kid"])
				}
				
				addresses[int(j["e.kid"])] = d
	res, commands, cmap = getCustom()
	for i in range(0,len(res)):

			j = {}
			
			for k in commands:
				j[k] = res[i][cmap[k]]
				
			if j["kaleidoaddr"] == ip:
				
				d = {
				"TOP": int(j["address1"]),
				"BOTTOM": int(j["address2"]),
				"C/N": 500 + int(j["input"]),
				"REC": 600 + int(j["input"])
				}
				
				addresses[int(j["input"])] = d
	return addresses

			

def getdb():
#	request = "SELECT s.servicename,s.aspectratio,s.ebno,s.pol,s.castatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,e.labelnamestatic,s.framerate FROM equipment e, status s WHERE e.id = s.id"
	request = "SELECT "
	commands = irdResult.commands
	
	cmap = {}
	for x in range(len(commands)):
		cmap[commands[x]] = x
	request += ",".join(commands)
	request += " FROM equipment e, status s WHERE e.id = s.id "
	
	gv.equip = {}
	for item in gv.sql.qselect(request):
		equipmentID = int(item[cmap["e.id"]])
		gv.[equipmentID] = irdResult(equipmentID, item)
	
	return gv.sql.qselect(request), commands, cmap
	
def writeDefaults():
	""" For blanking the canvas during UMD startup """
	res, commands, cmap = getdb()
	for i in range(0,len(res)):
			
			j = {}
			
			for k in commands:
				j[k] = res[i][cmap[k]]
			
			if (j["e.kaleidoaddr"] in mv.keys()):
				mv[j["e.kaleidoaddr"]].put( (int(j["e.kid"]), "TOP", 	j["e.labelnamestatic"], "TEXT")   )
				mv[j["e.kaleidoaddr"]].put( (int(j["e.kid"]), "BOTTOM", "", 			"TEXT")   )
				gv.labelcache[int(j["e.id"])] = {"TOP": j["e.labelnamestatic"], "BOTTOM":""}

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
		

def getrxes():
	""" Writes receiver results to multiviwer """
	res, commands, cmap = getdb()
	rxes = {}
	#print "%s RXES" % len(res)
	for i in range(0,len(res)):
			#print "Starting UMD for IRD " + str(i) + "/n"
			# nb python has no #DEFINE statement for constants, so these all get set as variables
			j = {}
			for k in commands:
				j[k] = res[i][cmap[k]]
			rxes[j["e.id"]] = j.copy()
	for equipmentID, rx in rxes.iteritems():
		
		if (rx["e.kaleidoaddr"] in mv.keys()):
			if rx["e.Demod"] != 0:
				if rxes.has_key(rx["e.Demod"]):
					if rx["s.asi"] in  ['IP', "ASI"]: #UNIT is using an external demod. Use that demod's settings 
						rx["s.asi"] = 'DEMOD'
						if rxes[rx["e.Demod"]]["s.status"] == "Online":
							for key in ['s.modulationtype', 's.channel', 's.pol', 's.ebno']:
							       rx[key] = rxes[rx["e.Demod"]][key]
			
			ebnoalarm = False
			#if unrx["s.muxstate"], rx either shows .-1 or 100.10db. For some reason TS lock state is not reliable so we work it out
			lockstate = "True"
			if any((rx["e.Demod"] != 0 , rx["s.asi"] == "SAT")):
				if (rx["s.ebno"] == ".-1dB"):
					lockstate = "False"
				elif ('-' in rx["s.ebno"]):
					lockstate = "False"
				elif (rx["s.ebno"] == "100.10dB"):
					lockstate = "False"
				elif (rx["s.ebno"] == "0.0dB"):
					lockstate = "False"
			if (len(rx["s.servicename"]) != 0): #clearly if there is a service name it is rx["s.muxstate"]
				lockstate = "True"
			if (rx["s.videostate"] == "Running"):
				lockstate = "True"
			if (rx["s.muxstate"] == "Unlock"):
				lockstate = "False"
			
			if rx["s.status"] == "Online":
				if (lockstate == "True"):
					bottomumd = ""
					topumd = ""
					# Let's go through and see if we are HD - and our SD resolution
					HD = False
					if (rx["s.videoresolution"] == "1080"): 
						HD = True
					elif (rx["s.videoresolution"] == "1088"): 
						HD = True	
						
					elif (rx["s.videoresolution"] == "720"):
						HD = True
					elif (rx["s.videoresolution"] == "576"):
						HD = False
						SD = "625"
					elif (rx["s.videoresolution"] == "480"):
						HD = False
						SD = "525"
					else:
						HD = False
						SD = ""
					framerate = rx["s.framerate"].replace(" ","")
					if remove_hz:
						framerate = framerate.replace("Hz","")
					# first set bottom display
					if (HD == True):
						bottomumd +=  rx["s.videoresolution"] + "/" + framerate
					else:
						if rx["s.aspectratio"] != "":
							if SD != "":
								bottomumd +=   SD[0] + "_"+rx["s.aspectratio"]
							else:
								bottomumd += rx["s.aspectratio"]
						else:
							bottomumd +=   SD
					
					if(rx["s.asi"] in ["ASI", "IP"]):
						text1 = rx["s.asi"]
					else:
						text1 = rx["s.ebno"]
						text1 = text1.replace('"','')
						text1 = text1.replace(' ','')
						text1 = text1.replace('+','')
						#ebnoalarm
						try:
							en = rx["s.ebno"]
							en = en.replace("dB","")
							
							ebnoint = float(en)
						except ValueError:
							ebnoint = 0 
						if ebnoint < 2:
							ebnoalarm = True
					
					bottomumd +=  "/" + text1 + " " + biss_status_text(rx["s.castatus"]) 
					
					
					
					#sendumd += "<setKDynamicText>set address=\""+rx["e.rx["e.labeladdr"]2"]+"\" text=\""+res[i][5]+" "+res[i][1]
					"""sendumd = sendumd + " " + res[i][2] + " " + res[i][3]+" Biss:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n" """
					#sendumd = sendumd + " / " + res[i][2] + " " +" BS:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n"
											# sendumd = sendumd + " / " + res[i][2] + " " +" BS:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n"
					
					
				else: #IF No lock, we write "NO LOCK" at the bottom
					bottomumd = "NO LOCK"
			else:	
				bottomumd="OFFLINE" 
								
									
			if rx["s.status"] == "Online":					
				#Are we in DVB-S or S2 mode?
				if (rx["s.asi"] != "ASI"): 
					
					dvbmode = rx["s.modulationtype"].replace("DVB-", "")
					
				# We need to get the mux bitrate we match it to a streamcode with a little leeway

				bitratestring = bitrateToStreamcode(rx["s.muxbitrate"])

				
									
				if (len(rx["s.channel"]) != 0): #Have we found the channel?
					if (lockstate == "True"): # Channel found and service running
						if (rx["s.asi"] != "ASI"): #NOT ASI
							rname = rx["e.labelnamestatic"].split(" ")[0].replace("RX","")
							toplabeltext = rname + " " + rx["s.channel"][0:max(0,(len(rx["s.channel"])-3))] + " " + bitratestring + "" + dvbmode + "| " + rx["s.servicename"]
						else:
							toplabeltext = rx["e.labelnamestatic"] + " " + bitratestring + ""  + "| " + rx["s.servicename"]
					else: #no input
						toplabeltext = rx["e.labelnamestatic"] + " " + rx["s.channel"] + "" + dvbmode

				else: # Channel missing and service running
					if (lockstate == "True"):
						toplabeltext = rx["e.labelnamestatic"] + " " + bitratestring + ""  + "| " + rx["s.servicename"]
					else:
						toplabeltext = rx["e.labelnamestatic"]
				
				
				
			else:
				toplabeltext = rx["e.labelnamestatic"]
								
								
								
								
			#sendumd += "<setKDynamicText>set address=\""+ rx["e.labeladdr"] +"\" text=\"" + toplabeltext + "\"</setKDynamicText>\n"
			#print "%s top: %s"% (rx["e.kid"], toplabeltext)

			mv[rx["e.kaleidoaddr"]].put( (int(rx["e.kid"]), "TOP", toplabeltext.replace("\n", ""), "TEXT")   )
			mv[rx["e.kaleidoaddr"]].put( (int(rx["e.kid"]), "BOTTOM", bottomumd.replace("\n", ""), "TEXT")   )
			
			gv.labelcache[int(rx["e.id"])] = {"TOP": toplabeltext.replace("\n", ""), "BOTTOM": bottomumd.replace("\n", "")}
			
			input = int(rx["e.kid"])
			d = {True:"MAJOR", False:"DISABLE"}
			#sendumd += '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>\n' %((input+ ebno_alarm_base), d[ebnoalarm])
			mv[rx["e.kaleidoaddr"]].put( (int(rx["e.kid"]), "C/N", d[ebnoalarm], "ALARM")   )
			#Truth Table If TVIPS and Omneon is enabled or if Omneon is enabled and the IRD does
			recalarm = any( (all( (bool(rx["s.OmneonRec"]), bool(rx["s.TvipsRec"]) )),
					all(( bool(rx["s.OmneonRec"]), bool(rx["e.doesNotUseGateway"]) ))
					) )
			d = {False:"MINOR", True:"DISABLE"}
			#sendumd += '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>\n' %((input+ rec_alarm_base), d[recalarm])
			mv[rx["e.kaleidoaddr"]].put( (int(rx["e.kid"]), "REC", d[recalarm], "ALARM")   )
			#print str(i), sendumd
			
		#print element
		#print sendumd
		#socketing(element,sendumd)
		
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
		



		

		
