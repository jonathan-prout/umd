#!/usr/bin/python
import os, re, sys


# changes oct 09
# added moudulation roll off symbol rate sat freq and FEC

class atom:
	def __init__(self,id,status,servicename,aspectratio,ebno,pol,bissstatus,vresol,framerate,vstate,asioutmode,inSatSetupModType,inSatSetupModType2,inSatSetupRollOff,inSatSetupSymbolRate,inSatSetupSatelliteFreq,inSatSetupFecRate,inSatSetupInputSelect,inSatSetupSatelliteFreq2,inSatSetupSymbolRate2,input_selection,inputTsBitrate):
		self.id = id
		self.status = status
		self.servicename = servicename
		self.aspectratio = aspectratio
		self.ebno = ebno
		self.pol = pol
		self.bissstatus = bissstatus
		self.vresol = vresol
		self.framerate = framerate
		self.vstate = vstate
		self.asioutmode = asioutmode
		self.inSatSetupModType = inSatSetupModType
		self.inSatSetupModType2 = inSatSetupModType2
		self.inSatSetupRollOff = inSatSetupRollOff
		self.inSatSetupSymbolRate = inSatSetupSymbolRate
		self.inSatSetupSatelliteFreq = inSatSetupSatelliteFreq
		self.inSatSetupFecRate = inSatSetupFecRate
		self.inSatSetupInputSelect = inSatSetupInputSelect
		self.inSatSetupSatelliteFreq2 = inSatSetupSatelliteFreq2
		self.inSatSetupSymbolRate2 = inSatSetupSymbolRate2
		self.input_selection = input_selection
		self.inputTsBitrate = inputTsBitrate
		
		
	def getId(self):
		return self.id
			
	def getServiceName(self):
		self.servicename = self.servicename.replace(';',' ')
		self.servicename = self.servicename.replace('%',' ')
		self.servicename = self.servicename.replace('&',' ')
		self.servicename = self.servicename.replace('*',' ')
		self.servicename = self.servicename.replace(',',' ')
		self.servicename = self.servicename.replace('?',' ')
		self.servicename = self.servicename.replace('{',' ')
		self.servicename = self.servicename.replace('}',' ')
		self.servicename = self.servicename.replace('(',' ')
		self.servicename = self.servicename.replace(')',' ')
		self.servicename = self.servicename.replace('[',' ')
		self.servicename = self.servicename.replace(']',' ')
		self.servicename = self.servicename.replace('^',' ')
		self.servicename = self.servicename.replace('+',' ')
		self.servicename = self.servicename.replace('|',' ')
		self.servicename = self.servicename.replace('-',' ')
		self.servicename = self.servicename.replace('_',' ')
		self.servicename = self.servicename.replace('"',' ')
		self.servicename = self.servicename.replace('\'',' ')
		self.servicename = self.servicename.replace('#',' ')
		self.servicename = self.servicename.replace(':',' ')
		self.servicename = self.servicename.replace('!',' ')
		self.servicename = self.servicename.replace('`',' ')
		self.servicename = self.servicename.replace('.',' ')
				
		return self.servicename
		
	def getAspectRatio(self):
		return self.aspectratio
	
	def getStatus(self):
		return self.status
	
	def getEbno(self):
		return self.ebno
	
	def getPol(self):
		return self.pol
	
	def getBissStatus(self):
		return self.bissstatus
	
	def getVResol(self):
		return self.vresol
	
	def getFrameRate(self):
		return self.framerate
	
	def getVState(self):
		return self.vstate
	
	def getAsioutMode(self):
		return self.asioutmode
# --		
	
	def getinSatSetupModType(self):
		return self.inSatSetupModType
		
	def getinSatSetupModType(self):
		return self.inSatSetupModType

	def getinSatSetupModType2(self):
		return self.inSatSetupModType2
		
	def getinSatSetupRollOff(self):
		return self.inSatSetupRollOff
	
	def getinSatSetupSymbolRate(self):
		return self.inSatSetupSymbolRate


	def getinSatSetupSatelliteFreq(self):
		return self.inSatSetupSatelliteFreq
		
	def getinSatSetupFecRate(self):
		return self.inSatSetupFecRate
		
	def getinputTsBitrate(self):
		return self.inputTsBitrate

	def getinSatSetupSymbolRate2(self):
		return self.inSatSetupSymbolRate2	


	def getinSatSetupSatelliteFreq2(self):
		return self.inSatSetupSatelliteFreq2
	
	def getinSatSetupInputSelect(self):
		return self.inSatSetupInputSelect

	def getinput_selection(self):
		return self.input_selection		
#--		
			
	def setId(self,id):
		self.id = id
	
	def setStatus(self,status):
		self.status = status
			
	def setServiceName(self,servicename):
		if (len(servicename) >=10):
			servicename = servicename[0:9]
		
		servicename = servicename.replace(';','')
		servicename = servicename.replace('&','')
		servicename = servicename.replace('-','')
		servicename = servicename.replace('"','')
		servicename = servicename.replace('\'','')
		servicename = servicename.replace('#','')
		servicename = servicename.replace(':','')
		servicename = servicename.replace('!','')
		servicename = servicename.replace('`','')
		servicename = servicename.replace('.','')
		self.servicename = servicename
		
	def setAspectRatio(self,aspectratio):
		if (aspectratio == "2"):
			self.aspectratio = "16:9"
		if (aspectratio == "3"):
			self.aspectratio = "4:3"
		if (aspectratio == ""):
			self.aspectratio = ""
			
	def setEbno(self,ebno):
		try:
			final = ebno[0:len(ebno)-2]+"."+ebno[:2]+"dB"
		except:
			final = ""
		if len(ebno) <= 1:
			final = ""
		self.ebno = final
	
	def setPol(self,pol):
		if (pol == "1"):
			self.pol = "Y"
		elif (pol == "2"):
			self.pol = "X"
		else:
			self.pol = ""
		
	def setBissStatus(self,bissstatus):
		if (bissstatus == "1"):
			self.bissstatus = "Off"
		elif (bissstatus == "2"):
			self.bissstatus = "On"
		else:
			self.bissstatus= ""
	
	def setVResol(self,vresol):
		self.vresol = vresol
		
	def setFrameRate(self,framerate):
		if (framerate == "1"):
			self.framerate = "Unknown"
		if (framerate == "2"):
			self.framerate = "25 Hz"
		if (framerate == "3"):
			self.framerate = "30 Hz"
		if (framerate == "4"):
			self.framerate = "50 Hz"
		if (framerate == "5"):
			self.framerate = "60 Hz"
		if (framerate == "6"):
			self.framerate = "29.97 Hz"
		if (framerate == "7"):
			self.framerate = "59.94 Hz"
			
	
	def setVState(self,vstate):
		if (vstate == "1"):
			self.vstate = "Running"
		if (vstate == "2"):
			self.vstate = "Stopped"
		if (vstate == "3"):
			self.vstate = "Errors"
		
		
	def setAsioutMode(self,asioutmode):
		if (asioutmode == "1"):
			self.asioutmode = "Disable"
		if (asioutmode == "2"):
			self.asioutmode = "Encrypted"
		if (asioutmode == "3"):
			self.asioutmode = "Patrially Decrypted"
		if (asioutmode == "4"):
			self.asioutmode = "Decrypted"
			
# JP Changes


		
	def setinSatSetupModType2(self,inSatSetupModType2):		
		self.inSatSetupModType2 = inSatSetupModType2
		
	def setinputTsBitrate(self,inputTsBitrate):
		self.inputTsBitrate = inputTsBitrate
		
	def setserviceID2(self,serviceID2):
		self.serviceID2 = serviceID2
		
	def setinput_selection(self,input_selection):
					
		
		if (input_selection == "1"):
			self.input_selection = "ASI"
		
		elif (input_selection == "2"):
			self.input_selection = "SAT"

		else:
			self.input_selection = ""

	def setinSatSetupSatelliteFreq2(self,inSatSetupSatelliteFreq2):
				self.inSatSetupSatelliteFreq2 = inSatSetupSatelliteFreq2

	def setinSatSetupInputSelect(self,inSatSetupInputSelect):
				self.inSatSetupInputSelect =inSatSetupInputSelect

	def setinSatSetupRollOff(self,inSatSetupRollOff):
		if (inSatSetupRollOff == "1"):
			self.inSatSetupRollOff= "0.20"
		if (inSatSetupRollOff == "2"):
			self.inSatSetupRollOff = "0.35"
		if (inSatSetupRollOff == "3"):
			self.inSatSetupRollOff = "0.25"	
	
	# IRD reports Symbolrate in SYMBOLS per second. D2S database in Kilosymbols
	# Must devide by 1000 for consistency
	
	def setinSatSetupModType(self,inSatSetupModType,inSatSetupModType2,inSatSetupInputSelect):
		if(inSatSetupInputSelect == "2"): #This is input 1 not 2	
			self.inSatSetupModType = inSatSetupModType
		else:
			self.inSatSetupModType = inSatSetupModType2
			
	def setinSatSetupSymbolRate(self,inSatSetupSymbolRate,inSatSetupSymbolRate2,inSatSetupInputSelect):
		symbolRateFloat = 0
		if(inSatSetupInputSelect == "2"): #This is input 1 not 2
			symbolRateFloat = float(inSatSetupSymbolRate)
		if(inSatSetupInputSelect == "3"): 
			symbolRateFloat = float(inSatSetupSymbolRate2)
		symbolRateFloat = (symbolRateFloat / 1000)
		finalsymrate = str(symbolRateFloat)
		##print finalsymrate
		if(finalsymrate[(len(finalsymrate)-2):] == ".0"):
			finalsymrate = finalsymrate[:(len(finalsymrate)-2)]
		self.inSatSetupSymbolRate = finalsymrate
		#print self.inSatSetupSymbolRate
		#self.inSatSetupSymbolRate = inSatSetupSymbolRate
	 

	def setinSatSetupSatelliteFreq(self,inSatSetupSatelliteFreq,inSatSetupSatelliteFreq2,inSatSetupInputSelect):
		#self.inSatSetupSatelliteFreq = inSatSetupSatelliteFreq 
			
		SatelliteFreqFloat = 0
				#print inSatSetupInputSelect
		if(inSatSetupInputSelect == "2"): #This is input 1 not 2
			SatelliteFreqFloat = float(inSatSetupSatelliteFreq)
		if(inSatSetupInputSelect == "3"): #This is input 2 not 3
			SatelliteFreqFloat = float(inSatSetupSatelliteFreq2)

				
		SatelliteFreqFloat = (SatelliteFreqFloat / 1000)
		finalSatelliteFreq = str(SatelliteFreqFloat)
				##print finalsymrate
				# This code is to compensate for inconsistencies in the D2S frequency table where
				# sometimes we have .0 at the end sometimes we don't
				# services.py then uses LIKE ...% to get it to match
		if(finalSatelliteFreq[(len(finalSatelliteFreq)-2):] == ".0"):
			finalSatelliteFreq = finalSatelliteFreq[:(len(finalSatelliteFreq)-2)]
		self.inSatSetupSatelliteFreq = finalSatelliteFreq
				#print self.inSatSetupSymbolRate
				#self.inSatSetupSymbolRate = inSatSetupSymbolRate

	# We may not need the FEC as most of the time our IRD can be in AUTO	
	def setinSatSetupFecRate(self,inSatSetupFecRate ):
		if (inSatSetupFecRate == "1"):
			self.inSatSetupFecRate= "0"
		if (inSatSetupFecRate == "2"):
			self.inSatSetupFecRate = "1/2"
		if (inSatSetupFecRate == "3"):
			self.inSatSetupFecRate = "2/3"	
		if (inSatSetupFecRate == "4"):
			self.inSatSetupFecRate= "3/4"
		if (inSatSetupFecRate == "5"):
			self.inSatSetupFecRate = "5/6"
		if (inSatSetupFecRate == "6"):
			self.inSatSetupFecRate = "6/7"	
		if (inSatSetupFecRate == "7"):
			self.inSatSetupFecRate= "7/8"
		if (inSatSetupFecRate == "8"):
			self.inSatSetupFecRate = "8/9"
		if (inSatSetupFecRate == "9"):
			self.inSatSetupFecRate = "Auto"	
