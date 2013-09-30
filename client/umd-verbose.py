#!/usr/bin/python
import os, re, string,threading
import sys,time,datetime
import mysql
import socket
import getopt

ASI_MODE_TEXT = "ASI"
remove_hz = True

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
	if any(loud, errors_in_stdout):
			print "**** ERROR!! ******"
			print "\n".join(errortext)
			print "***********************"
	file = open(logfile,"a")
	errortext.append(" ")
	file.write("\n".join(errortext))
	file.close()	

def socketing(host,msg):
	
	now = datetime.datetime.now()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		
		PORT = 13000			  # The same port as used by the server
		
		s.connect((host, PORT))
		s.send(msg)
		data = s.recv(1024)
		s.close()
		
	except:
		now = datetime.datetime.now()
		errortext = []
		errortext.append("Socket error at " + now.strftime("%d-%m-%Y %H:%M:%S") )
		
		errortext += [host,msg]
		logwrite(errortext)

		
	  #print 'Received', repr(data)
	
	 # print "Opening socket: ",host,msg
	finally:
		s.close()
	
def main():
	now = datetime.datetime.now()
	
	mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
	mysql.mysql.mutex = threading.RLock()
	sql = mysql.mysql()

	res = ""
	
#	request = "SELECT s.servicename,s.aspectratio,s.ebno,s.pol,s.bissstatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,e.labelnamestatic,s.framerate FROM equipment e, status s WHERE e.id = s.id"
	request = "SELECT s.servicename,s.aspectratio,s.ebno,s.pol,s.bissstatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,s.channel,s.framerate,e.labelnamestatic,s.modulationtype,s.modtype2,s.asi,s.videoresolution,e.model_id,s.muxbitrate,s.videostate FROM equipment e, status s WHERE e.id = s.id"
#									   0			 	 1				 	2	 		3		 4			 		5		    			6				7			 8			9		   10		   11				 12			      13		14	   15				 16          17          18

	try:
		res = sql.qselect(request)
	except MySQLdb.Error, e:
		errortext = []
		now = datetime.datetime.now()
		errortext.append("SQL Connection Error at %s" % now.strftime("%d-%m-%Y %H:%M:%S") )
		errortext.append( "Error %d: %s" % (e.args[0], e.args[1]))
		
		logwrite(errortext)
		
	finally:
		sql.close()
		
	
	
	indexmatrix=[]
	vmatrix={}
		

	for i in range(0,len(res)):
		if (res[i][7] not in indexmatrix):
			"res[i][7] are kaleido host..."
			if loud:
				print "res[i][7]",res[i][7]
			indexmatrix.append(res[i][7])
			
	


   
	
	
	threads=[]
	for element in indexmatrix:
		
		if loud:
			print "Building command for " +element
		sendumd =""
		vmatrix[element]=[]
		for i in range(0,len(res)):
			
			
			kaleidoaddr	  = res[i][7]

			
			if (element == kaleidoaddr):
				""" s.servicename,s.aspectratio,s.ebno,s.pol,s.bissstatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,e.labelnamestatic,s.framerate """
				try:	
					servicename	  = res[i][0]
					aspectratio	  = res[i][1]
					ebno			 = res[i][2]
					pol			  = res[i][3]
					bissstatus	   = res[i][4]
					matrixname	   = res[i][5]
					labeladdr2	   = res[i][6]

					labeladdr		= res[i][8]
					channelname	  = res[i][9]
					framerate		= res[i][10]
					labelnamestatic  = res[i][11]
					modulationtype   = res[i][12]
					modtype2		 = res[i][13]
					asi			  = res[i][14]
					videoresolution  = res[i][15]
					model_id		 = res[i][16]
					muxbitrate		 = res[i][17]
					videostate 		 = res[i][18]	
					"""
					if loud:
						print "Starting UMD for IRD " + str(i) 
					"""	
					#if unlocked, rx either shows .-1 or 100.10db. For some reason TS lock state is not reliable so we work it out
					lockstate = "true"
					badebno = False
					if (ebno == ".-1dB"):
						lockstate = "false"
						badebno = True
						
					if (ebno == "100.10dB"):
						lockstate = "false"
						badebno = True
					if (len(servicename) != 0): #clearly if there is a service name it is locked
						lockstate = "true"
						if badebno:
							asi = "ASI"
					if (videostate == "Running"):
						lockstate = "true"
						if badebno:
							asi = "ASI"


					if (lockstate == "true"):

						# Let's go through and see if we are HD - and our SD resolution
						HD = False
						if (videoresolution == "1080"): 
							HD = True
						elif (videoresolution == "720"):
							HD = True
						elif (videoresolution == "576"):
							HD = False
							SD = "6"
						elif (videoresolution == "480"):
							HD = False
							SD = "5"
						else:
							HD = False
							SD = ""

						if remove_hz:
							framerate = framerate.replace("Hz","")
						# first set bottom display
						if (HD == True):
							sendumd += "<setKDynamicText>set address=\"" + labeladdr2 + "\" text=\"" + videoresolution + "/" + framerate
						else:
							sendumd += "<setKDynamicText>set address=\"" + labeladdr2 + "\" text=\"" + SD + "_"+aspectratio
						
						# Displays ASI if the IRD is on ASI otherwise displays the ebno on the bottom.
						# Only works on 1290s - but since no 1260 here is on ASI that is a moot bug.
						if(asi == "ASI"):
							text1 = ASI_MODE_TEXT
						else:
							text1 = ebno
						bissstatus = biss_status_text(bissstatus)
						
						sendumd = sendumd + "/" + text1 + " " + bissstatus + "\"</setKDynamicText>\n"
						
						
						#sendumd += "<setKDynamicText>set address=\""+labeladdr2+"\" text=\""+res[i][5]+" "+res[i][1]
						"""sendumd = sendumd + " " + res[i][2] + " " + res[i][3]+" Biss:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n" """
						#sendumd = sendumd + " / " + res[i][2] + " " +" BS:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n"
												# sendumd = sendumd + " / " + res[i][2] + " " +" BS:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n"

					else: #IF No lock, we write "NO LOCK" at the bottom
						sendumd += "<setKDynamicText>set address=\"" + labeladdr2 + "\" text=\"NO LOCK\" </setKDynamicText>\n"
						

										
											
										
						#Are we in DVB-S or S2 mode?
					if (asi != "ASI"): 
						# in order to confuse us - the 1260 and 1290 report different numbers. So ask Model ID
						if (model_id == 1): # TT1260
							if (modulationtype == 2): #Modulationtype asks the receiver modtype2 asks the database so we ask modulationtype first
								dvbmode = "S"
							elif (modulationtype == 5):
								dvbmode = "S2"
							elif (modtype2 == "DVB-S"):
								dvbmode = "S"
							elif (modtype2 == "DVB-S2"):
								dvbmode = "S2"
							else:
								dvbmode = ""
						elif (model_id == 3): # RX1290	
							if (modulationtype == 1): 
								dvbmode = "S"
							elif (modulationtype == 2):
								dvbmode = "S2"
							elif (modtype2 == "DVB-S"):
								dvbmode = "S"
							elif (modtype2 == "DVB-S2"):
								dvbmode = "S2"
							else:
								dvbmode = ""
						else:
							dvbmode = ""
					else:
						dvbmode = ""

					# We need to get the mux bitrate we match it to a streamcode with a little leeway
					try:
						bitratefloat = float(muxbitrate)
						bitratefloat = (bitratefloat / 1000000) #bps to mbps
					except:
						bitratefloat = 0
					if (bitratefloat < 1):
						bitratestring = ""
					elif(7  < bitratefloat < 7.5):
						bitratestring = "7"
					elif(8.4  < bitratefloat < 8.5):
						bitratestring = "8+"
					elif(10.7  < bitratefloat < 10.76):
						bitratestring = "11"
					elif(15.6  < bitratefloat < 15.7):
						bitratestring = "16"
					elif(21.4  < bitratefloat < 21.6):
						bitratestring = "22"
					elif(31.3  < bitratefloat < 31.4):
						bitratestring = "32"
					elif(41.7  < bitratefloat < 41.9):
						bitratestring = "42"
					elif(60.3  < bitratefloat < 60.5):
						bitratestring = "60"
					else:
						bitratestring = str(bitratefloat)[:4]


										
					if (len(channelname) != 0): #Have we found the channel?
						if (lockstate == "true"): # Channel found and service running
							toplabeltext = labelnamestatic[:1] + " " + channelname[0:(len(channelname)-3)] + " " + bitratestring + "" + dvbmode + "| " + servicename
						else: #no input
							toplabeltext = labelnamestatic + " " + channelname + "" + dvbmode

					else: # Channel missing and service running
						toplabeltext = labelnamestatic + " " + servicename

										
										
										
										
					sendumd += "<setKDynamicText>set address=\""+ labeladdr +"\" text=\"" + toplabeltext + "\"</setKDynamicText>\n" 

				except:
					errortext = []
					now = datetime.datetime.now()
					errortext.append("Error Building text command from database at %s" % now.strftime("%d-%m-%Y %H:%M:%S") )
					errortext.append("IRD = %s" % i )
					errortext.append("servicename = %s" % res[i][0])
					errortext.append("aspectratio	   = %s" % res[i][1])
					errortext.append("ebno			  = %s" % res[i][2])
					errortext.append("pol			   = %s" % res[i][3])
					errortext.append("bissstatus	    = %s" % res[i][4])
					errortext.append("matrixname	    = %s" % res[i][5])
					errortext.append("labeladdr2	    = %s" % res[i][6])
					
					errortext.append("labeladdr		 = %s" % res[i][8])
					errortext.append("channelname	   = %s" % res[i][9])
					errortext.append("framerate		 = %s" % res[i][10])
					errortext.append("labelnamestatic   = %s" % res[i][11])
					errortext.append("modulationtype    = %s" % res[i][12])
					errortext.append("modtype2		  = %s" % res[i][13])
					errortext.append("asi			   = %s" % res[i][14])
					errortext.append("videoresolution   = %s" % res[i][15])
					errortext.append("model_id		  = %s" % res[i][16])
					errortext.append("muxbitrate		  = %s" % res[i][17])
					errortext.append("videostate 		  = %s" % res[i][18])
					logwrite(errortext)
			#print element
			#print sendumd
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
	#exit

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