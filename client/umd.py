#!/usr/bin/python
import os, re, string,threading
import sys,time,datetime
import mysql
import socket


def socketing(host,msg):
	
	now = datetime.datetime.now()
	
	try:
		
		PORT = 13000              # The same port as used by the server
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
	request = "SELECT s.servicename,s.aspectratio,s.ebno,s.pol,s.bissstatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,s.channel,s.framerate,e.labelnamestatic FROM equipment e, status s WHERE e.id = s.id"

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
			sendumd =""
			vmatrix[element]=[]
			for i in range(0,len(res)):
				if (element == res[i][7]):
					""" s.servicename,s.aspectratio,s.ebno,s.pol,s.bissstatus, e.matrixname,e.labeladdr2,e.kaleidoaddr,e.labeladdr,e.labelnamestatic,s.framerate """
					
					"res[i][2] are signal/noise ratio... if 0 no transmission, otherwise there are info to display..."
					if (len(res[i][2]) != 0):
						"""sendumd += "<setKDynamicText>set address=\""+res[i][6]+"\" text=\""+res[i][5]+" "+res[i][0]+" "+res[i][1]"""
						
						sendumd += "<setKDynamicText>set address=\""+res[i][6]+"\" text=\""+res[i][5]+" "+res[i][1]
						"""sendumd = sendumd + " " + res[i][2] + " " + res[i][3]+" Biss:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n" """
						#sendumd = sendumd + " / " + res[i][2] + " " +" BS:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n"
                                                sendumd = sendumd + " / " + res[i][2] + " " +" BS:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n"

					else:
						#sendumd += "<setKDynamicText>set address=\""+res[i][6]+"\" text=\""+res[i][5]+" "+" "+" "+res[i][1]
						#sendumd = sendumd + " " + res[i][2] + " " + res[i][3]+" "+res[i][4]+"\"</setKDynamicText>\n"
					        #sendumd = sendumd + " " + res[i][2] + " "+res[i][4]+"\"</setKDynamicText>\n"
                                                sendumd += "<setKDynamicText>set address=\""+res[i][6]+"\" text=\"NO LOCK\" </setKDynamicText>\n"

					servicename = res[i][0]
					#if (len(servicename) == 0):
					#		servicename = "NO INPUT"
					channelname = str(res[i][9])
                                        receivername = str(res[i][11])
                                        if (len(channelname) != 0):
                                            if (len(res[i][2]) != 0):
                                                        text1 = channelname
                                                        text2 = servicename
                                            else: #no input
                                                        text1 = receivername
                                                        text2 = channelname
                                        else:
                                             text1 = receivername
                                             text2 = servicename	
					sendumd += "<setKDynamicText>set address=\""+res[i][8]+"\" text=\""+text1+" "+text2+"\"</setKDynamicText>\n" 
					#print str(i), sendumd
			print element
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
