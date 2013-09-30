#!/usr/bin/python

import sys,os,commands,string, subprocess
import getopt,atom,encoderatom

""" OCT 09 added 
		inSatSetupModType =""
		inSatSetupSatelliteFreq =""
		inSatSetupSymbolRate =""
		inSatSetupFecRate =""
		
"""
def askSN_AR(thiscommand,id,model):
	"""
	(status, out) = commands.getstatusoutput(thiscommand)
	#print out
	lines = string.split(out,"\n")
	#i = 0	 
	#for l in lines:
		#print i,":",l
		#i = (i+1)
		#print lines[9]
	res = string.find(lines[0],"Timeout")
	#print "self->model:",model
	#if (model == 1):
	
	if (res == -1):
	"""
	try:
		out = subprocess.check_output(thiscommand)
		#print out
		lines = string.split(out,"\n")
		#i = 0	 
		#for l in lines:
			#print i,":",l
			#i = (i+1)
			#print lines[9]
		res = string.find(lines[0],"Timeout")
		if (res == -1):
			raise "Timeout"
	except CalledProcessError, "Timeout":
	
		# decoder part
		servicename =""
		aspectratio =""
		ebno =""
		pol =""
		bissstatus=""
		vresol =""
		framerate=""
		vstate = ""
		asioutmode =""
		inSatSetupModType =""
		inSatSetupSatelliteFreq =""
		inSatSetupSymbolRate =""
		inSatSetupFecRate =""
		inSatSetupRollOff =""
		inSatSetupInputSelect =""
		inSatSetupSatelliteFreq2 =""
		inSatSetupSymbolRate2 =""
		input_selection = ""
		dvbS2InputNumber = ""
		inSatSetupModType2 = ""
		inputtsbitrate = ""
		serviceID = ""
		serviceID2 = ""
		# encoder part
		muxbitrate=""
		muxscrambling =""
		muxbissword=""
		muxencryptedword=""
		videoprofilelevel=""
		muxstate=""
		videobitrate=""
		videopid=""
		videoaspectratio =""
		videogoplen=""
		videogopstruc=""
		videobandwidth=""
		videomaxbitrate=""
		videodelay=""
		temperature=""
		pol2=""
		lockState=""
	else:	
		try:
			if (model == 1):
				serviceID = lines[0][1:]
				aspectratio = lines[1][1:]
				ebno = lines[2][1:]
				pol = lines[3][1:]
				bissstatus = lines[4][1:]
				vresol = lines[5][1:]
				framerate = lines[6][1:]
				vstate = lines[7][1:]
				asioutmode = lines[8][1:]
				inSatSetupModType = lines[9][1:]
				inSatSetupSatelliteFreq = lines[10][1:]
				inSatSetupSymbolRate = lines[11][1:]
				inSatSetupFecRate = lines[12][1:]
				inSatSetupInputSelect = lines[13][1:]
				inSatSetupSatelliteFreq2 = lines[14][1:]
				inSatSetupSymbolRate2  = lines[15][1:]
				inSatSetupModType2  = lines[16][1:]
				inputTsBitrate  = lines[17][1:]
				pol2   = lines[18][1:]
				lockState = lines[19][1:]
				input_selection = ""
				#print inputTsBitrate

			if (model == 3):
				servicename = lines[0][1:]
				aspectratio = lines[1][1:]
				ebno = lines[2][1:]
				pol = lines[3][1:]
				bissstatus = lines[4][1:]
				vresol = lines[5][1:]
				framerate = lines[6][1:]
				vstate = lines[7][1:]
				asioutmode = lines[8][1:]
				inSatSetupModType = lines[9][1:]
				inSatSetupSatelliteFreq = lines[10][1:]
				inSatSetupSymbolRate = lines[11][1:]
				inSatSetupFecRate = lines[12][1:]
				inSatSetupInputSelect = lines[13][1:]
				inSatSetupSatelliteFreq2 = lines[14][1:]
				inSatSetupSymbolRate2  = lines[15][1:]
				inSatSetupRollOff = lines[16][1:]
				input_selection  = lines[17][1:]
				inSatSetupModType2  = lines[18][1:]
				inputTsBitrate  = lines[19][1:]
				pol2   = lines[20][1:]
				lockState = lines[21][1:]
				#print inputTsBitrate
			if (model == 4):
				serviceID = lines[0][1:]  
				aspectratio = lines[1][1:] 
				ebno = lines[2][1:] #k
				pol = lines[3][1:] #k
				bissstatus = lines[4][1:] 
				vresol = lines[5][1:] 
				framerate = lines[6][1:] 
				vstate = lines[7][1:] 
				asioutmode = lines[8][1:] 
				inSatSetupModType = lines[9][1:]  
				inSatSetupSatelliteFreq = lines[10][1:] 
				inSatSetupSymbolRate = lines[11][1:]
				inSatSetupFecRate = lines[12][1:]
				inSatSetupInputSelect = lines[13][1:]
				dvbS2InputNumber = lines[14][1:] #new
				inSatSetupRollOff = lines[15][1:]
				input_selection  = lines[16][1:]
				inputTsBitrate  = lines[17][1:]
				lockState = lines[18][1:]
				#print inputTsBitrate
			if (model == 2):
				
				servicename = lines[0][1:]
				muxbitrate = lines[1][1:len(lines[1])]
				muxscrambling = lines[2][1:len(lines[2])]
				muxbissword =lines[3][1:len(lines[3])]
				muxencryptedword = lines[4][1:len(lines[4])]
				videoprofilelevel = lines[5][1:len(lines[5])]
				muxstate = lines[6][1:len(lines[6])]
				videobitrate=lines[7][1:len(lines[7])]
				videopid =lines[8][1:len(lines[8])]
				videoaspectratio =lines[9][1:len(lines[9])]
				videogoplen =lines[10][1:len(lines[10])]
				videogopstruc =lines[11][1:len(lines[11])]
				videobandwidth =lines[12][1:len(lines[12])]
				videomaxbitrate =lines[13][1:len(lines[13])]
				videodelay = lines[14][1:len(lines[14])]
				temperature = lines[15][1:len(lines[15])]	

				"""
					print "lines ",lines
				print "lines[0]",lines[0]				
				print "servicename ",servicename
				print "muxbitrate ",muxbitrate
				print "muxscrambling ",muxscrambling
				print "muxencryptedword ",muxencryptedword
				print "videoprofilelevel ",videoprofilelevel
				print "muxstate ",muxstate
				print "videobitrate ", videobitrate
				print "videopid ",videopid
				print "videoaspectratio ", videoaspectratio
				print "videogoplen ", videogoplen
				print "videogopstruc ", videogopstruc
				print "videobandwidth ",videobandwidth
				print "videomaxbitrate ",videomaxbitrate
				print "videodelay ", videodelay
				"""
					
		except IndexError,e :
			servicename =""
			aspectratio =""
			ebno =""
			pol =""
			bissstatus=""
			vresol =""
			framerate=""
			vstate = ""
			asioutmode =""
			muxbitrate=""
			muxscrambling =""
			muxbissword=""
			muxencryptedword=""
			videoprofilelevel=""
			muxstate=""
			videobitrate=""
			videopid=""
			videoaspectratio =""
			videogoplen=""
			videogopstruc=""
			videobandwidth=""
			videomaxbitrate=""
			videodelay=""
			temperature=""
			
			
		if (model == 1):
			obj = atom.atom("","","","","","","","","","","","","","","","","","","","","","","","")
			obj.model = model
			obj.setStatus("on")
			obj.setId(id)
			obj.setServiceName(servicename)
			obj.setAspectRatio(aspectratio)
			obj.setEbno(ebno)
			obj.setPol(pol,pol2,inSatSetupInputSelect)
			obj.setBissStatus(bissstatus)
			obj.setVResol(vresol)
			obj.setFrameRate(framerate)
			obj.setVState(vstate)
			obj.setAsioutMode(asioutmode)
			obj.setinSatSetupModType(inSatSetupModType,inSatSetupModType2,inSatSetupInputSelect)
			obj.setinSatSetupRollOff(inSatSetupRollOff)
			obj.setinSatSetupModType2(inSatSetupModType2)
			obj.setinputTsBitrate(inputTsBitrate)
			#obj.setserviceID2(serviceID2)
			obj.setinput_selection(0)

			obj.setinSatSetupFecRate(inSatSetupSymbolRate)
			obj.setinSatSetupInputSelect(inSatSetupInputSelect)
			obj.setinSatSetupSatelliteFreq2(inSatSetupSatelliteFreq2)
			obj.setinSatSetupSymbolRate(inSatSetupSymbolRate,inSatSetupSymbolRate2,inSatSetupInputSelect)
			obj.setinSatSetupSatelliteFreq(inSatSetupSatelliteFreq,inSatSetupSatelliteFreq2,inSatSetupInputSelect)
			obj.setpol2(pol2)
			obj.setlockState(lockState)
			return obj
		if (model == 3):
			obj = atom.atom("","","","","","","","","","","","","","","","","","","","","","","","")
			obj.model = model
			obj.setStatus("on")
			obj.setId(id)
			obj.setServiceName(servicename)
			obj.setAspectRatio(aspectratio)
			obj.setEbno(ebno)
			obj.setPol(pol,pol2,inSatSetupInputSelect)
			obj.setBissStatus(bissstatus)
			obj.setVResol(vresol)
			obj.setFrameRate(framerate)
			obj.setVState(vstate)
			obj.setAsioutMode(asioutmode)
			obj.setinSatSetupModType(inSatSetupModType,inSatSetupModType2,inSatSetupInputSelect)
			obj.setinSatSetupRollOff(inSatSetupRollOff)
			
			
			obj.setinSatSetupModType2(inSatSetupModType2)
			obj.setinputTsBitrate(inputTsBitrate)
			#obj.setserviceID2(serviceID2)
			obj.setinSatSetupFecRate(inSatSetupFecRate)
			obj.setinSatSetupInputSelect(inSatSetupInputSelect)
			obj.setinput_selection(input_selection)
			obj.setinSatSetupSatelliteFreq2(inSatSetupSatelliteFreq2)
			obj.setinSatSetupSatelliteFreq(inSatSetupSatelliteFreq,inSatSetupSatelliteFreq2,inSatSetupInputSelect)
			obj.setinSatSetupSymbolRate(inSatSetupSymbolRate,inSatSetupSymbolRate2,inSatSetupInputSelect)
			obj.setpol2(pol2)
			obj.setlockState(lockState)
			return obj			
		if (model == 2):
			obj = encoderatom.encoderatom("","","","","","","","","","","","","","","","","","")
			obj.model = model
			obj.setId(id)
			obj.setStatus("on")
			obj.setServiceName(servicename)
			obj.setMuxBitRate(muxbitrate)
			obj.setMuxScrambling(muxscrambling)
			obj.setMuxBissWord(muxbissword)
			obj.setMuxEncryptedWord(muxencryptedword)
			obj.setVideoProfileLevel(videoprofilelevel)
			obj.setMuxStatus(muxstate)
			obj.setVideoBitRate(videobitrate)
			obj.setVideoPid(videopid)
			obj.setVideoAspectRatio(videoaspectratio)
			obj.setVideoGOPLen(videogoplen)
			obj.setVideoGOPStruc(videogopstruc)
			obj.setVideoBandwidth(videobandwidth)
			obj.setVideoMaxBitrate(videomaxbitrate)
			obj.setVideoDelay(videodelay)
			obj.setTemperature(temperature)
			#obj = atom.atom(servicename,aspectratio)
			return obj
	else:
		#print "IRD is offline"
		if (model == 1):
			obj = atom.atom("","","","","","","","","","","","","","","","","","","","","","","")
			obj.model = model
			obj.setId(id)
			obj.setStatus("off")
			obj.setEbno('')
			obj.setPol("")
			obj.setBissStatus("")
			obj.setVResol("")
			obj.setFrameRate("")
			obj.setVState("")
			obj.setAsioutMode("")
			obj.setinSatSetupModType2("")
			obj.setinputTsBitrate("")
			obj.setserviceID2("")
			obj.setinSatSetupModType("")
			obj.setinSatSetupModType2("")
			obj.setinSatSetupRollOff("")
			obj.setinSatSetupSymbolRate("")
			obj.setinSatSetupSatelliteFreq("")
			obj.setinSatSetupFecRate("")
			obj.setinput_selection("")		
			obj.setpol2("")
			obj.setlockState("")
			return obj
		if (model == 3):
			obj = atom.atom("","","","","","","","","","","","","","","","","","","","")
			obj.model = model
			obj.setId(id)
			obj.setStatus("off")
			obj.setEbno('')
			obj.setPol("")
			obj.setBissStatus("")
			obj.setVResol("")
			obj.setFrameRate("")
			obj.setVState("")
			obj.setAsioutMode("")
			obj.setinSatSetupModType("")
			obj.setinSatSetupRollOff("")	
			obj.setinSatSetupSymbolRate("")
			obj.setinSatSetupSatelliteFreq("")
			obj.setinSatSetupFecRate("")
			obj.setinput_selection("")	
			obj.setinSatSetupModType2("")
			obj.setinputTsBitrate("")
			obj.setserviceID2("")
			obj.setpol2("")
			obj.setlockState("")			
			return obj
		if (model == 4):
			obj = atom.atom("","","","","","","","","","","","","","","","","","","","")
			obj.model = model
			obj.setId(id)
			obj.setStatus("off")
			obj.setEbno('')
			obj.setPol("")
			obj.setBissStatus("")
			obj.setVResol("")
			obj.setFrameRate("")
			obj.setVState("")
			obj.setAsioutMode("")
			obj.setinSatSetupModType("")
			obj.setinSatSetupRollOff("")	
			obj.setinSatSetupSymbolRate("")
			obj.setinSatSetupSatelliteFreq("")
			obj.setinSatSetupFecRate("")
			obj.setinput_selection("")	
			obj.setinSatSetupModType2("")
			obj.setinputTsBitrate("")
			obj.setserviceID2("")
			obj.setpol2("")
			obj.setlockState("")			
			return obj
			
		if (model == 2):
			obj = encoderatom.encoderatom("","","","","","","","","","","","","","","","","","","")
			obj.model = model
			obj.setId(id)
			obj.setStatus("off")
			obj.setServiceName("")
			obj.setMuxBitRate("")
			obj.setMuxScrambling("")
			obj.setMuxBissWord("")
			obj.setMuxEncryptedWord("")
			obj.setVideoProfileLevel("")
			obj.setMuxStatus("")
			obj.setVideoBitRate("")
			obj.setVideoPid("")
			obj.setVideoAspectRatio("")
			obj.setVideoGOPLen("")
			obj.setVideoGOPStruc("")
			obj.setVideoBandwidth("")
			obj.setVideoMaxBitrate("")
			obj.setVideoDelay("")			
			obj.setTemperature("")
			"""
			if (model == 2):
				 obj = encoderatom.encoderatom("","","","","","","","","","","","","","","","")
				 return obj
			"""
 
def snmp_walk(ip, command):
	commandlist = ["/usr/bin/snmpwalk", "-v 1", "-c public", ip, command] 
	try:
		output = subprocess.check_output(commandlist)
	except CalledProcessError:
		return []
	
	returnlist = []
	lines = output.split('\n')
	for line in lines:
		if ":" in line:
			line = line.split(':')[1]
		line = line.strip('"')
		line = line.strip()
		returnlist.append(line)
	return returnlist
	
class equipment:
	
	def __init__(self,id,model,ip,name,network,matrixname):
		self.id = id
		self.model = model
		self.ip = ip
		self.name = name
		self.network = network
		self.matrixname = matrixname
	
	def getIp(self):
		return self.ip
		
	def getId(self):
		return self.id
		
	def getModel(self):
		return self.model
		
		
	def getSNMP(self,newcommand):
		#print "NEW_COMMAND",newcommand
		syscommand_p1 = r"/usr/bin/snmpget -v 1 -c public "
		#syscommand_p2 = r"  enterprises.1773.1.3.200.2.4.3.0   enterprises.1773.1.3.200.3.1.1.6.0  | awk -F'=' '{print $2}' | awk -F':' '{print $2}' | sed s/\"//g"
		syscommand_p2 = r"   | awk -F'=' '{print $2}' | awk -F':' '{print $2}' | sed s/\"//g"
		sendcommand = syscommand_p1  + self.ip + newcommand + syscommand_p2
		#if (self.model == 3):
		#print sendcommand
		#pass
		#if (self.model == 1):
		#print sendcommand
		#pass
		#print self.model
		""" IRD """
		if (self.model == 1):
			myatom = atom.atom("","","","","","","","","","","","","","","","","","","","","","","","")
		""" ENCODER """
		if (self.model == 2):
			myatom = encoderatom.encoderatom("","","","","","","","","","","","","","","","","","")
		if (self.model == 3):
			myatom = atom.atom("","","","","","","","","","","","","","","","","","","","","","","","")
		myatom = askSN_AR(sendcommand,self.id,self.model)
		return myatom
		
