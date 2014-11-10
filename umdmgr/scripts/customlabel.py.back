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
	
	request = "SELECT * FROM `customlabel`"

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
			if (res[i][2] not in indexmatrix):
				"res[i][2] are kaleido host..."
				print "res[i][2]",res[i][2]
				indexmatrix.append(res[i][2])
				
	
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
				id	  = res[i][0]
				name	  = res[i][1]
				kaleidoaddr			 = res[i][2]
				labeladdr			  = res[i][3]
				text	   = res[i][4]
				
				
				if (element == kaleidoaddr):

					sendumd += "<setKDynamicText>set address=\"" + labeladdr + "\" text=\"" + text + "\" </setKDynamicText>\n"
						

					print str(i), sendumd
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
