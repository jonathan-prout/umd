#!/usr/bin/python
import os, re, string,threading
import sys,time,datetime
import mysql
import socket

# why doesn't true or false have meaning in Python?
true = 1
false = 0


def socketing(host,msg):
	
	now = datetime.datetime.now()
	
	try:
		
		PORT = 13000			  # The same port as used by the server
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, PORT))
		s.send(msg)
		data = s.recv(1024)
		s.close()
		print host,msg
	except:
		now = datetime.datetime.now()
		print "Socket error at ", now.strftime("%H:%M:%S")
		pass
	  #print 'Received', repr(data)
	
	 # print "Opening socket: ",host,msg

	
if __name__ == "__main__":
	now = datetime.datetime.now()
	
	mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
	mysql.mysql.mutex = threading.RLock()
	sql = mysql.mysql()

	res = ""
	
#	request = "SELECT s.servicename,s.aspectratio,s.ebno,s.pol,s.bissstatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,e.labelnamestatic,s.framerate FROM equipment e, status s WHERE e.id = s.id"
	request = "SELECT s.servicename,s.aspectratio,s.ebno,s.pol,s.bissstatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,s.channel,s.framerate,e.labelnamestatic,s.modulationtype,s.modtype2,s.asi,s.videoresolution,e.model_id,s.muxbitrate,s.videostate FROM equipment e, status s WHERE e.id = s.id"
#					   0			  1				 2	 3		 4			 5		    	6			7			 8			9		   10		   11				 12			      13		14	   15				 16          17          18

	try:
		res = sql.qselect(request)
	except MySQLdb.Error, e:
		print "SQL Connection Error at ",now.strftime("%H:%M:%S")
		print "Error %d: %s" % (e.args[0], e.args[1])
	sql.close()
		
	
	
	indexmatrix=[]
	vmatrix={}
		
	try:
		for i in range(0,len(res)):
			if (res[i][7] not in indexmatrix):
				"res[i][7] are kaleido host..."
				print "res[i][7]",res[i][7]
				indexmatrix.append(res[i][7])
				
	
	except:
		print "Error catched"
   
	try:
	
		threads=[]
		for element in indexmatrix:
			print element
			sendumd =""
			vmatrix[element]=[]
			for i in range(0,len(res)):
				print "Starting UMD for IRD " + str(i) + "/n"
				# nb python has no #DEFINE statement for constants, so these all get set as variables 
				servicename	  = res[i][0]
				aspectratio	  = res[i][1]
				ebno			 = res[i][2]
				pol			  = res[i][3]
				bissstatus	   = res[i][4]
				matrixname	   = res[i][5]
				labeladdr2	   = res[i][6]
				kaleidoaddr	  = res[i][7]
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
				
				if (element == kaleidoaddr):
					""" s.servicename,s.aspectratio,s.ebno,s.pol,s.bissstatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,e.labelnamestatic,s.framerate """
					
					#if unlocked, rx either shows .-1 or 100.10db. For some reason TS lock state is not reliable so we work it out
					lockstate = "true"
					if (ebno == ".-1dB"):
						lockstate = "false"
					if (ebno == "100.10dB"):
						lockstate = "false"
					if (len(servicename) != 0): #clearly if there is a service name it is locked
						lockstate = "true"
					if (videostate == "Running"):
						lockstate = "true"
					
					
					
					if (lockstate == "true"):
					
						# Let's go through and see if we are HD - and our SD resolution
						HD = false
						if (videoresolution == "1080"): 
							HD = true
						elif (videoresolution == "720"):
							HD = true
						elif (videoresolution == "576"):
							HD = false
							SD = "6"
						elif (videoresolution == "480"):
							HD = false
							SD = "5"
						else:
							HD = false
							SD = ""
					
					
						# first set bottom display
						if (HD == true):
							sendumd += "<setKDynamicText>set address=\"" + labeladdr2 + "\" text=\"" + videoresolution + "/" + framerate
						else:
							sendumd += "<setKDynamicText>set address=\"" + labeladdr2 + "\" text=\"" + SD + "_"+aspectratio
						
						# Displays ASI if the IRD is on ASI otherwise displays the ebno on the bottom.
						# Only works on 1290s - but since no 1260 here is on ASI that is a moot bug.
						if(asi == "ASI"):
							text1 = asi
						else:
							text1 = ebno
						
						
						sendumd = sendumd + " / " + text1 + " " +" BS:" + bissstatus + "\"</setKDynamicText>\n"
						
						
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
					#print str(i), sendumd
			#print element
			#print sendumd
			thread = threading.Thread(None,target=socketing,args=[element,sendumd])	
			threads.append(thread)
			thread.start()
			#threads.join()
			
		for t in threads:
			t.join()
		exit

	except:
		print "Index error at ", now.strftime("%H:%M:%S")
	
		pass
