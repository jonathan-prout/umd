#!/usr/bin/python
import os, re, string,threading
import sys,time,datetime
import mysql
import socket
import socket
import getopt

ASI_MODE_TEXT = "ASI"
remove_hz = True
ebno_alarm_base = 500
rec_alarm_base = 600


logfile = "/var/www/programming/client/client_error.txt"
loud = False
errors_in_stdout = False


def biss_status_text(bissstatus):
	if bissstatus == "On":
		return "BS:ON"
	elif bissstatus == "Off":
		return "BS:Off"
	else:
		return ""

		
		
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



def socketing(host,msg):
	
	now = datetime.datetime.now()
	
	try:
		
		PORT = 13000			  # The same port as used by the server
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, PORT))
		s.send(msg)
		data = s.recv(1024)
		s.close()
		if loud:
			print host,msg
	except:
		now = datetime.datetime.now()
		print "Socket error at ", now.strftime("%H:%M:%S")
		pass
	  #print 'Received', repr(data)
	
	 # print "Opening socket: ",host,msg


def bitrateToStreamcode(muxbitrate):
	tolerance = float(0.125)
	#streamcodes == []:
	streamcodes = sql.qselect("SELECT `name`, `bitrate` FROM `streamcodes` WHERE 1")
	
	
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
	
def main():
	global sql
	now = datetime.datetime.now()
	
	mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
	mysql.mysql.mutex = threading.RLock()
	sql = mysql.mysql()
	
	global streamcodes
	res = ""
	
#	request = "SELECT s.servicename,s.aspectratio,s.ebno,s.pol,s.bissstatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,e.labelnamestatic,s.framerate FROM equipment e, status s WHERE e.id = s.id"
	request = "SELECT "
	commands = ["s.servicename","s.aspectratio","s.ebno","s.pol",
		    "s.bissstatus","e.labeladdr2","e.kaleidoaddr",
		    "e.labeladdr","s.channel","s.framerate","e.labelnamestatic",
		    "s.modulationtype","s.modtype2","s.asi","s.videoresolution",
		    "e.model_id","s.muxbitrate","s.videostate", "s.status", "s.muxstate", "m.input",
		    "s.OmneonRec", "s.TvipsRec", "e.doesNotUseGateway"]
	
	cmap = {}
	for x in range(len(commands)):
		cmap[commands[x]] = x
	request += ",".join(commands)
	request += " FROM equipment e, status s, multiviewer_map m WHERE e.id = s.id AND e.id = m.equipmentID"

	res = sql.qselect(request)
	
	
		
	
	
	indexmatrix=[]
	vmatrix={}
		
	try:
		for i in range(0,len(res)):
			if (res[i][cmap["e.kaleidoaddr"]] not in indexmatrix):
				"res[i][7] are kaleido host..."
				if loud:
					print "Kaleido ",res[i][cmap["e.kaleidoaddr"]]
				indexmatrix.append(res[i][cmap["e.kaleidoaddr"]])
				
	
	except:
		print "Error catched"
   
	#try:

	threads=[]
	for element in indexmatrix:
		#print element
		sendumd =""
		vmatrix[element]=[]
		for i in range(0,len(res)):
			#print "Starting UMD for IRD " + str(i) + "/n"
			# nb python has no #DEFINE statement for constants, so these all get set as variables
			j = {}
			for k in commands:
				j[k] = res[i][cmap[k]]
			"""
			#This may get cleaned up later
			
			
			servicename	  = res[i][cmap["s.servicename"]]
			aspectratio	  = res[i][cmap["s.aspectratio"]]
			ebno			 = res[i][cmap["s.ebno"]]
			pol			  = res[i][cmap["s.pol"]]
			bissstatus	   = res[i][cmap["s.bissstatus"]]
			#matrixname	   = res[i][cmap["e.kaleidoaddr"]]
			labeladdr2	   = res[i][cmap["e.labeladdr2"]]
			kaleidoaddr	  = res[i][cmap["e.kaleidoaddr"]]
			labeladdr		= res[i][cmap["e.labeladdr"]]
			channelname	  = res[i][cmap["s.channel"]]
			framerate		= res[i][cmap["s.framerate"]]
			labelnamestatic  = res[i][cmap["e.labelnamestatic"]]
			modulationtype   = res[i][cmap["s.modulationtype"]]
			locked   	 = res[i][cmap["s.muxstate"]]
			asi			  = res[i][cmap["s.asi"]]
			videoresolution  = res[i][cmap["s.videoresolution"]]
			model_id		 = res[i][cmap["e.model_id"]]
			muxbitrate		 = res[i][cmap["s.muxbitrate"]]
			videostate 		 = res[i][cmap["s.videostate"]]
			online 			=  res[i][cmap["s.status"]]
			online 			=  res[i][cmap["s.status"]]
			OmneonRec	=  bool(res[i][cmap["s.OmneonRec"]])
			TvipsRec	=  bool(res[i][cmap["s.TvipsRec"]])
			doesNotUseGateway	=  bool(res[i][cmap["e.doesNotUseGateway"]])
			kal_input =  res[i][cmap["m.input"]]
			"""
			
			if (element == j["e.kaleidoaddr"]):
				""" s.j["s.servicename"],s.j["s.aspectratio"],s.j["s.ebno"],s.j["s.pol"],s.j["s.bissstatus"], e.matrixname,e.j["e.j["e.labeladdr"]2"],e.j["e.kaleidoaddr"],e.j["e.labeladdr"],e.j["e.labelnamestatic"],s.j["s.framerate"] """
				ebnoalarm = False
				#if unj["s.muxstate"], rx either shows .-1 or 100.10db. For some reason TS lock state is not reliable so we work it out
				lockstate = "True"
				if (j["s.ebno"] == ".-1dB"):
					lockstate = "False"
				elif ('-' in j["s.ebno"]):
					lockstate = "False"
				elif (j["s.ebno"] == "100.10dB"):
					lockstate = "False"
				if (len(j["s.servicename"]) != 0): #clearly if there is a service name it is j["s.muxstate"]
					lockstate = "True"
				if (j["s.videostate"] == "Running"):
					lockstate = "True"
				if (j["s.muxstate"] == "Unlock"):
					lockstate = "False"
				
				if j["s.status"] == "Online":
					if (lockstate == "True"):
					
						# Let's go through and see if we are HD - and our SD resolution
						HD = False
						if (j["s.videoresolution"] == "1080"): 
							HD = True
						elif (j["s.videoresolution"] == "1088"): 
							HD = True	
							
						elif (j["s.videoresolution"] == "720"):
							HD = True
						elif (j["s.videoresolution"] == "576"):
							HD = False
							SD = "6"
						elif (j["s.videoresolution"] == "480"):
							HD = False
							SD = "5"
						else:
							HD = False
							SD = ""
						framerate = j["s.framerate"].replace(" ","")
						if remove_hz:
							framerate = framerate.replace("Hz","")
						# first set bottom display
						if (HD == True):
							sendumd += "<setKDynamicText>set address=\"" + j["e.labeladdr2"] + "\" text=\"" + j["s.videoresolution"] + "/" + framerate
						else:
							sendumd += "<setKDynamicText>set address=\"" + j["e.labeladdr2"] + "\" text=\"" + SD + "_"+j["s.aspectratio"]
						
						
						if(j["s.asi"] == "ASI"):
							text1 = j["s.asi"]
						else:
							text1 = j["s.ebno"]
							#ebnoalarm
							try:
								ebnoint = float(j["s.ebno"].replace("dB",""))
							except ValueError:
								ebnoint = 0 
							if ebnoint < 2:
								ebnoalarm = True
						
						sendumd = sendumd + "/" + text1 + " " +" BS:" + j["s.bissstatus"] + '"</setKDynamicText>\n'
						
						
						#sendumd += "<setKDynamicText>set address=\""+j["e.j["e.labeladdr"]2"]+"\" text=\""+res[i][5]+" "+res[i][1]
						"""sendumd = sendumd + " " + res[i][2] + " " + res[i][3]+" Biss:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n" """
						#sendumd = sendumd + " / " + res[i][2] + " " +" BS:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n"
												# sendumd = sendumd + " / " + res[i][2] + " " +" BS:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n"
						
						
					else: #IF No lock, we write "NO LOCK" at the bottom
						sendumd += "<setKDynamicText>set address=\"" + j["e.labeladdr2"] + "\" text=\"NO LOCK\" </setKDynamicText>\n"
				else:	
					sendumd += '<setKDynamicText>set address="' + j["e.labeladdr2"] + '" text="OFFLINE" </setKDynamicText>\n'
									
										
				if j["s.status"] == "Online":					
					#Are we in DVB-S or S2 mode?
					if (j["s.asi"] != "ASI"): 
						# in order to confuse us - the 1260 and 1290 report different numbers. So ask Model ID
						dvbmode = j["s.modulationtype"].replace("DVB-", "")
						
					# We need to get the mux bitrate we match it to a streamcode with a little leeway

					bitratestring = bitrateToStreamcode(j["s.muxbitrate"])

					
										
					if (len(j["s.channel"]) != 0): #Have we found the channel?
						if (lockstate == "True"): # Channel found and service running
							if (j["s.asi"] != "ASI"): #NOT ASI
								toplabeltext = j["e.labelnamestatic"][:1] + " " + j["s.channel"][0:max(0,(len(j["s.channel"])-3))] + " " + bitratestring + "" + dvbmode + "| " + j["s.servicename"]
							else:
								toplabeltext = j["e.labelnamestatic"] + " " + bitratestring + ""  + "| " + j["s.servicename"]
						else: #no input
							toplabeltext = j["e.labelnamestatic"] + " " + j["s.channel"] + "" + dvbmode

					else: # Channel missing and service running
						if (lockstate == "True"):
							toplabeltext = j["e.labelnamestatic"] + " " + bitratestring + ""  + "| " + j["s.servicename"]
						else:
							toplabeltext = j["e.labelnamestatic"]
					
					
					
				else:
					toplabeltext = j["e.labelnamestatic"]
									
									
									
									
				sendumd += "<setKDynamicText>set address=\""+ j["e.labeladdr"] +"\" text=\"" + toplabeltext + "\"</setKDynamicText>\n"
				input = int(j["m.input"])
				d = {True:"MAJOR", False:"DISABLE"}
				sendumd += '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>\n' %((input+ ebno_alarm_base), d[ebnoalarm])
				
				#Truth Table If TVIPS and Omneon is enabled or if Omneon is enabled and the IRD does
				recalarm = any( (all( (bool(j["s.OmneonRec"]), bool(j["s.TvipsRec"]) )),
						all(( bool(j["s.OmneonRec"]), bool(j["e.doesNotUseGateway"]) ))
						) )
				d = {False:"MINOR", True:"DISABLE"}
				sendumd += '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>\n' %((input+ rec_alarm_base), d[recalarm])
				#print str(i), sendumd
				
		#print element
		#print sendumd
		#socketing(element,sendumd)

	
	
		try:
			
			thread = threading.Thread(None,target=socketing,args=[element,sendumd])	
			thread.KaleidoIP = element
			threads.append(thread)
			if loud:
				print "Starting thread " +element
			thread.start()
		
		except:	
			errortext = []
			now = datetime.datetime.now()
			errortext.append("Thread Error at %s" % now.strftime("%d-%m-%Y %H:%M:%S") )
			errortext += [element,sendumd]
			logwrite(errortext)
	if loud:
		print "Waiting for %s threads to finish" % len(threads)
	for t in threads:
		if loud:
			print "joining " + str(t.KaleidoIP)
		t.join(10)
		if t.isAlive():
			errortext = []
			now = datetime.datetime.now()
			errortext.append("Thread TimeOut at %s" % now.strftime("%d-%m-%Y %H:%M:%S") )
			errortext.append("Thread Handled %s" %	t.KaleidoIP)
			logwrite(errortext)
	sql.close()
	

def usage():
	print "v, verbose logs everything"
	print "l, loop, loops every 10s"
	print "e, errors, print errors"
		
if __name__ == "__main__":
	try:                                
		opts, args = getopt.getopt(sys.argv[1:], "vle", ["verbose", "loop", "errors"]) 
	except getopt.GetoptError, errr:
		print str(err)	
		print "error in arguments"
		usage()                          
		sys.exit(2) 
	#verbose = False
	loop = False
	
	for opt, arg in  opts:
	
		if opt in ("-v", "--verbose"):
			loud = True
		elif opt in ("-l", "--loop"):
			loop = True
		elif opt in ("-e", "--errors"):
			errors_in_stdout = True
		else:
			print opt
			assert False, 'option not recognised' 

	if loud:
		print "Starting in verbose mode"
	running = True
	try:
		while running:
			
			now = datetime.datetime.now()
			if loud:
				print "starting " + now.strftime("%d-%m-%Y %H:%M:%S")
			main()
			now = datetime.datetime.now()
			if loud:
				print "Done " + now.strftime("%d-%m-%Y %H:%M:%S")
			
			if not loop:
				running = False
			if running:
				time.sleep(10)
	except KeyboardInterrupt:
		running = False
		print "You pressed control c, so I am quitting"