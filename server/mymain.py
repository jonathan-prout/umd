#!/usr/bin/python

import os, re, sys
import string,threading,time
import equipment,atom,services
import mysql


def getSNMP(equipmentobj):
	global sql
	snmp_commands = ""
	com = ""
	mid = equipmentobj.getModel()
	
	comsel ="SELECT model_param,model_command FROM model_command WHERE model_id = %i" % mid
	try:
		snmp_command = sql.qselect(comsel)
		for i in range(0,len(snmp_command)):
			com = " "+snmp_command[i][1]+" "
			snmp_commands += com
	except:
		raise "DB error"
		 	
	atomobj = equipmentobj.getSNMP(snmp_commands)
	#print snmp_commands
	if (mid == 1):
		updatesql = "UPDATE status SET status = '%s' , servicename = '%s', aspectratio ='%s', ebno='%s', pol='%s', bissstatus='%s', videoresolution='%s', framerate='%s',videostate='%s',asioutmode='%s',frequency='%s',symbolrate='%s',fec='%s',rolloff='%s',modulationtype='%s',muxbitrate='%s' WHERE id = %i; " %(atomobj.getStatus(),atomobj.getServiceName(),atomobj.getAspectRatio(),atomobj.getEbno(),atomobj.getPol(),atomobj.getBissStatus(),atomobj.getVResol(),atomobj.getFrameRate(),atomobj.getVState(),atomobj.getAsioutMode(),atomobj.getinSatSetupSatelliteFreq(),atomobj.getinSatSetupSymbolRate(),atomobj.getinSatSetupFecRate(),atomobj.getinSatSetupRollOff(),atomobj.getinSatSetupModType(),atomobj.getinputTsBitrate(),atomobj.getId())
		print updatesql
	if (mid == 3):
		#updatesql = "UPDATE status SET status = '%s' , servicename = '%s', aspectratio ='%s', ebno='%s', pol='%s', bissstatus='%s', videoresolution='%s', framerate='%s',videostate='%s',asioutmode='%s'  WHERE id = %i; " %(atomobj.getStatus(),atomobj.getServiceName(),atomobj.getAspectRatio(),atomobj.getEbno(),atomobj.getPol(),atomobj.getBissStatus(),atomobj.getVResol(),atomobj.getFrameRate(),atomobj.getVState(),atomobj.getAsioutMode(),atomobj.getId())
		updatesql = "UPDATE status SET status = '%s' , servicename = '%s', aspectratio ='%s', ebno='%s', pol='%s', bissstatus='%s', videoresolution='%s', framerate='%s',videostate='%s',asioutmode='%s',frequency='%s',symbolrate='%s',fec='%s',rolloff='%s',modulationtype='%s',asi='%s',muxbitrate='%s' WHERE id = %i; " %(atomobj.getStatus(),atomobj.getServiceName(),atomobj.getAspectRatio(),atomobj.getEbno(),atomobj.getPol(),atomobj.getBissStatus(),atomobj.getVResol(),atomobj.getFrameRate(),atomobj.getVState(),atomobj.getAsioutMode(),atomobj.getinSatSetupSatelliteFreq(),atomobj.getinSatSetupSymbolRate(),atomobj.getinSatSetupFecRate(),atomobj.getinSatSetupRollOff(),atomobj.getinSatSetupModType(),atomobj.getinput_selection(),atomobj.getinputTsBitrate(),atomobj.getId())

	if (mid == 2):
		updatesql = "UPDATE status SET servicename ='%s', status = '%s', muxbitrate='%s',muxscrambling ='%s', muxbissword ='%s', \
		muxencryptedword = '%s', videoprofilelevel ='%s', muxstate ='%s', videobitrate='%s',  \
		videopid ='%s', videoaspectratio ='%s', videogoplen='%s',videogopstruc='%s', \
		videobandwidth='%s', videomaxbitrate ='%s', videodelay='%s', temperature='%s'  WHERE id = %i;  " %(atomobj.getServiceName(),atomobj.getStatus(),atomobj.getMuxBitRate(),atomobj.getMuxScrambling(), \
		atomobj.getMuxBissWord(),atomobj.getMuxEncrypedWord(),atomobj.getVideoProfileLevel(),atomobj.getMuxStatus(), \
		atomobj.getVideoBitRate(),atomobj.getVideoPid(),atomobj.getVideoAspectRatio(),atomobj.getVideoGOPLen(), \
		atomobj.getVideoGOPStruc(),atomobj.getVideoBandwidth(),atomobj.getVideoMaxBitrate(),atomobj.getVideoDelay(),atomobj.getTemperature(),atomobj.getId()) 
		#print updatesql
	del atomobj
	try:
		#print updatesql
		msg = sql.qselect(updatesql)
	except:
		raise "stoppping..."
		exit


	

def retrivalList():
	global sql
	globallist = []
	request = "select * FROM equipment"
	try:
		Results = sql.qselect(request)
		for i in range(0,len(Results)):
			""" id, model_id, ip, name, network  """
			obj = equipment.equipment(Results[i][0],Results[i][1],Results[i][2],Results[i][3],Results[i][4],Results[i][5])
			globallist.append(obj)
			del obj
		del Results
		return globallist
	except:
		raise "Oooppp...."
		return NULL
	
	
""" call getSnmp function for each equipment, argument is equipment object itself (polymorphism)"""


mysql.mysql.semaphore = threading.BoundedSemaphore(value=3)
mysql.mysql.mutex = threading.RLock()
sql = mysql.mysql()

thislist = []
thislist = retrivalList() 
threads = []


for x in thislist:
	thread = threading.Thread(None,target=getSNMP,args=[x])
	threads.append(thread)
	thread.start()

for t in threads:
	t.join()
sql.close()

services.service()
