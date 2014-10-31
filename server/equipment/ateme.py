from generic import IRD, GenericIRD
import gv
class DR5000(IRD):
	""" ATEME DR5000 version 1.0.2.2 """
	def __init__(self, equipmentId, ip, name):
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "DR5000"
		super( DR5000, self ).__init__()
	def getAspectRatio(self):
		""" NOT IMPLIMENTED ON ATEME """
		#d = {"2":"16:9","3":"4:3"}
		#return self.lookup_replace('aspect ratio', d)
		return ""
	
	def getServiceName(self):
		try:
			Table_Service_ID = list(self.snmp_res_dict["Table_Service_ID"])
			Table_Service_Name = list(self.snmp_res_dict["Table_Service_Name"])
			ServiceID = self.getServiceId()
		except KeyError:
			return  ""
		for x in xrange(len(Table_Service_ID)):
			try:
				Table_Service_ID[x] = int(Table_Service_ID[x])
			except ValueError:
				try:
					v = Table_Service_ID[x]
					v = v.replace('"','')
					v = v.replace('\n','')
					v = v.replace(' ','')
					Table_Service_ID[x] = int(v)
				except ValueError:
					Table_Service_ID[x] = -1
		try:
			
			d = dict(zip(Table_Service_ID, Table_Service_Name))
			
			serviceName = d[ServiceID]
			return self.processServiceName(serviceName)
		except:
			return ""
	
	def getServiceId(self):
		try:
			return int(self.lookupstr('service_id'))
		except ValueError:
			return 0
	
	def getEbno(self):
		""" 0 = unlock
		164 = 16.4db """
		ebno = self.lookupstr('Eb / No')
		try:
			ebno = float(ebno)/10
		except ValueError:
			ebno = 0.0
		val = "%.1fdB"%ebno
		return str(val)
	
	def getPol(self):
		d = {"1":"Y","2":"X"}
		return self.lookup_replace('polarisation', d)
	
	def getCAStatus(self):
		""" True or False """
		"""Syntax	 TruthValue 1 true 2 false"""
		return  self.lookupstr("dr5000StatusDecodeCurrentProgramScrambled") == "1"

	def getBissStatus(self):
		
		"""biss1(2),
		bisse1(3),
		bisse2(4)
		"""
		
		"""JP 08/01/2013 IRD does not return the correct result on SNMP Poll
		d = {"1":"Off","2":"On","3":"On","4":"On"}
		if self.getCAStatus():
			return self.lookup_replace('Biss Status', d)
		else:
			return "Off"
		"""
		return ""
	

	def getFrameRate(self):
		try:
			numerator = int( self.lookupstr('frame rate num') )
		except ValueError:
			numerator = 0.0
		try:
			denominator = int( self.lookupstr('frame rate den') )
		except ValueError:
			denominator = 1.0
		try:
			qty =  float(numerator / denominator)
		except ZeroDivisionError:
			qty = 0
		return ("%.2fHz"%qty).replace(".00","")
		
		
	def getVResol(self):
		
		return self.lookupstr('video vertical resolution')
	
	def getinput_selection(self):
		""" Input type"""
		k = "dr5000StatusInputType"
		d = {"1":"IP", "2":"ASI", "3":"SAT", "4":"DS3"}
		return self.lookup_replace(k,d)

	def getlockState(self):
		""" return True on Bitrate when not using SAT"""
		if self.getinput_selection() == "SAT":
			d = {"1":"Lock","2":"Unlock"}
			return self.lookup_replace('SatLockState', d)
		else:
			stat = ["Unlock", "Lock"] 
			return stat[int(self.getinputTsBitrate()) > 0]

	def getinputTsBitrate(self):
		""" in kbps """
		
		key = 'inputtsbitrate'
		try:
			d = int(self.lookupstr(key)) * 1000 #kbps to bps
		except ValueError:
			d = 0
		return d
		
		
		#return int(self.lookupstr("inputtsbitrate")) * 1000 #kbps to bps

		




	def getinSatSetupModType(self):
		key = 'dr5000StatusInputSatModulation'
		d = {"1":"unknown","2":"qpsk","3":"8psk","4":"16apsk","5":"32apsk"}
		return self.lookup_replace(key, d)

	def getinSatSetupInputSelect(self):
		""" DR5000 """
		key = 'dr5000ChannelConfigurationInputSatInterface'
		inp = self.lookupstr(key)
		try:
			return int(inp)  
		except ValueError:
			return 1
	def getinSatSetupRollOff(self):
		
		d = {"4":"0.20","2":"0.35","3":"0.25","1":"0"}
		return self.lookup_replace('dr5000StatusInputSatRollOff', d)    


	def getVState(self):
		d = {"1":"Running","2":"Stopped"}
		return self.lookup_replace('video state', d)
	
	def getAsioutMode(self):
			d = {"1":"Decrypted","2":"Encrypted" }
			return self.lookup_replace('asi output mode', d)
	def getinSatSetupSatelliteFreq(self):
		""" Take kHz Return MHz """
		hz = 100000
		khz = 1000
		try:
			SatelliteFreqFloat = float(self.lookupstr('inSatSetupSatelliteFreq'))
		except ValueError: 
			SatelliteFreqFloat = 0
						
		SatelliteFreqFloat = (SatelliteFreqFloat / khz)
		finalSatelliteFreq = str(SatelliteFreqFloat)
						##print finalsymrate
						# This code is to compensate for inconsistencies in the D2S frequency table where
						# sometimes we have .0 at the end sometimes we don't
						# services.py then uses LIKE ...% to get it to match
		if(finalSatelliteFreq[(len(finalSatelliteFreq)-2):] == ".0"):
				finalSatelliteFreq = finalSatelliteFreq[:(len(finalSatelliteFreq)-2)]
		return finalSatelliteFreq
	def getinSatSetupSymbolRate(self):
			""" Take KSPS return KSPS """
			key = "inSatSetupSymbolRate"
			try:
				symbolRateFloat = float(self.lookupstr(key))
			except ValueError:
				symbolRateFloat = 0
			symbolRateFloat = (symbolRateFloat )
			finalsymrate = str(symbolRateFloat)
			##print finalsymrate
			if(finalsymrate[(len(finalsymrate)-2):] == ".0"):
					finalsymrate = finalsymrate[:(len(finalsymrate)-2)]
			return finalsymrate
	def getinSatSetupFecRate(self):
		"""Return FEC rate. Normally Auto"""
		
		d = {"1":"unknown","2":"1/4","3":"1/3","4":"2/5","5":"1/2","6":"3/5","7":"2/3",
			 "8":"3/4","9":"4/5","10":"5/6","11":"6/7","12":"7/8","13":"8/9","14":"9/10"}
		return self.lookup_replace('SatStatusFEC', d) 
	def updatesql(self):
		sql =  "UPDATE status SET status = '%s' , "% self.getStatus()
		sql += "servicename = '%s', "% self.getServiceName()
		sql += "aspectratio ='%s', "% self.getAspectRatio()
		sql += "ebno='%s', "% self.getEbno()
		sql += "pol='%s', "% self.getPol()
		sql += "bissstatus='%s', "% self.getBissStatus()
		sql += "videoresolution='%s', "% self.getVResol()
		sql += "framerate='%s', "% self.getFrameRate()
		sql += "videostate='%s',"% self.getVState()
		sql += "asioutmode='%s',"% self.getAsioutMode()
		sql += "frequency='%s',"% self.getinSatSetupSatelliteFreq()
		sql += "symbolrate='%s',"% self.getinSatSetupSymbolRate()
		sql += "fec='%s',"% self.getinSatSetupFecRate()
		sql += "rolloff='%s',"% self.getinSatSetupRollOff()
		sql += "modulationtype='%s',"% self.getinSatSetupModType()
		sql += "asi='%s',"% self.getinput_selection()
		sql += "muxbitrate='%s', "% self.getinputTsBitrate()
		sql += "muxstate='%s' ,"% self.getlockState()
		sql += "sat_input='%i'"% self.getinSatSetupInputSelect()
		sql += "WHERE id = %i; " %self.getId()
		return sql