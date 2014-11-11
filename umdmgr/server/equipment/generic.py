from server import gv

from helpers import snmp
snmp.gv = gv #in theory we don't want to import explictly the server's version of gv
class equipment(object):
	def getoid(self):
		""" Obtains SNMP Paramaters for ModelType according to database"""
		
		""" First time this is called these will not exist so we need to intitialize them but not make them blank if we ever call this more than once """
		try:
			unused = self.oid_get.keys()
		except AttributeError:
			self.oid_get = {}
		try:
			unused = self.oid_getBulk.keys()
		except AttributeError:
			self.oid_getBulk = {}
		
		comsel ="SELECT model_param,model_command FROM model_command WHERE model_id = '%s' AND mode = 'GET'" % self.modelType
		comsel_bulk ="SELECT model_param,model_command FROM model_command WHERE model_id = '%s' AND mode = 'GETBULK'" % self.modelType
		"""
		snmp_command = gv.sql.qselect(comsel)
		for i in range(len(snmp_command)):
			self.oid_get[snmp_command[i][0]] =snmp_command[i][1]
		"""
		try:
			snmp_command = gv.sql.qselect(comsel)
			for i in range(len(snmp_command)):
				self.oid_get[snmp_command[i][0]] =snmp_command[i][1]    
		except:
			raise "DB Error: 'Get SNMP COMMANDS'"
		try:
			snmp_command = gv.sql.qselect(comsel_bulk)
			for i in range(len(snmp_command)):
				self.oid_getBulk[snmp_command[i][0]] =snmp_command[i][1]
					
		except:
			raise "DB Error: 'Get SNMP BULK COMMANDS'"
		#self.oid_get2 = self.oid_get #there is a bug that overwrites self.oid_get. I can't find it
		#gv.sql.close()
		
	def refresh(self):
		""" Refresh method of class """
		""" removed import snmp here """
		try:
			self.snmp_res_dict  = snmp.get(self.getoids(), self.ip)
		except:
			self.set_offline()
		if len(self.snmp_res_dict.keys()) < len(self.getoids().keys()):
			self.oid_mask()

		if len(self.snmp_res_dict) == 0:
			self.set_offline()
		if len(self.oid_getBulk) !=0:
			self.snmp_res_dict.update( snmp.walk(self.bulkoids(), self.ip) )
	def getId(self):
		return self.equipmentId       
	def oid_mask(self):
		pass

	def getoids(self):
		return dict(self.oid_get)
	def oid_get_function(self):
		return self.oid_get2
	def bulkoids(self):
		return self.oid_getBulk

	def lookup(self, key):
		try:
			return  self.snmp_res_dict[key]
		except KeyError:
			return ""
	def lookupstr(self, key):
		return str(self.lookup(key))
	
	def lookup_replace(self, key, d):
		try:
			r = self.snmp_res_dict[key]
		except KeyError:
			r = ""
		for func in (str, int):
			try:
				
				return d[func(r)]
			except KeyError:
				continue
			except ValueError:
				continue
		return ""

	def determine_type(self):
		""" determine Type. Returns string and
		should be processed outside the class as the idea is to replace with the correct device class"""
		
		""" removed import snmp here """ 
		#d = {'DeviceType':".1.3.6.1.4.1.1773.1.1.1.7.0"}
		equipTypes = [
			[
                                {'DeviceType': ".1.3.6.1.4.1.27338.5.2.2.0"}
                                 ,"testing whether it's an  Ateme",
                                "DR5000"
                        ],[
                                {'DeviceType':  ".1.3.6.1.4.1.37576.2.3.1.5.1.2.1"} #This is not the best but then that is not on older versions of NS mib
                                 ,"testing whether it's a  Novelsat",
                                "NS2000"
                        ],[
				{'DeviceType':".1.3.6.1.2.1.1.1.0"},#sysdescr.0
				 "testing whether it's a Tandberg or TVIPS",
				""
			]
		]
		
		def type_test(equipTypes):
			for test, blurb, setType in equipTypes:
				ver_found = False
				try:
					#if gv.loud: print(blurb)
					resdict  = snmp.get(test, self.ip)
					assert( resdict != {} )
					if setType != "":
						resdict['DeviceType'] = setType
					
					self.offline = False
					
					ver_found = True
					return resdict, ver_found
					
				except:
					pass
		
				
			if not ver_found:
				self.offline = True
				resdict = {'DeviceType':"OFFLINE"}
				ver_found = False
			return resdict, ver_found
		sysdesc = {'DeviceType':".1.3.6.1.2.1.1.1.0"} #sysdescr.0
		nov_soft_ver = {'DeviceType': ".1.3.6.1.4.1.37576.2.3.1.5.1.2.1"} #This is not the best but then that is not on older versions of NS mib
		
		
		
		
			#resdict  = snmp.get({'DeviceType':".1.3.6.1.4.1.1773.1.1.1.7.0"}, self.ip)
		resdict, ver_found = type_test(equipTypes)
			
		if resdict.has_key('DeviceType'):
			return resdict['DeviceType']
		else:
			if gv.loud:
				print resdict
			self.offline = True
			return "OFFLINE"
	def determine_subtype(self):
		"""  Gets a unit's subtype if required. Override if the unit actually has a subtype"""
		try:
			return self.modelType
		except:
			return "Unknown"
	def set_offline(self):
		self.offline = True

	def get_offline(self):
		try:
			return self.offline
		except:
			return True
	def min_refresh_time(self):
		return gv.min_refresh_time
			
class IRD(equipment):
	def __init__(self):
		self.oid_get = {}
		self.getoid()
		self.snmp_res_dict = {}
		self.sat_dict = {}
		self.offline = False
		self.masked_oids = {}
		
		
	def oid_mask(self):
		try:
			masks = self.masked_oids[self.getinSatSetupInputSelect()]
		except KeyError:
			masks = []
		for key in self.oid_get.keys():
			if not self.snmp_res_dict.has_key(key):
				if gv.loud:
					print "Unit returned no such name for %s so masking"%key
				masks.append(key)
		self.masked_oids[self.getinSatSetupInputSelect()] = masks
		
	def getoids(self):

		dic =  self.oid_get.copy()
		try:
			masks = self.masked_oids[self.getinSatSetupInputSelect()]
		except KeyError:
			masks = []
			
		for k, v in dic.items():
			v = v.replace('enterprises.','.1.3.6.1.4.1.')
			v = v.replace('X', str(self.getinSatSetupInputSelect()))
			if k in masks:
				del dic[k]
			else:
				dic[k] = v
		#if self.getinSatSetupInputSelect() = 1:
		#    print "%s is on imput %s"%(self.name, self.getinSatSetupInputSelect())
		return dic
	
	def bulkoids(self):
		return self.oid_getBulk
	
	def getServiceName(self):
		try:
			serviceName = self.snmp_res_dict["service name"]
		except KeyError:
			serviceName = ""
		return self.processServiceName(serviceName)
	
	def processServiceName(self, servicename):
		servicename = servicename.strip()
		servicename = servicename.replace(';',' ')
		servicename = servicename.replace('%',' ')
		servicename = servicename.replace('&',' ')
		servicename = servicename.replace('*',' ')
		servicename = servicename.replace(',',' ')
		servicename = servicename.replace('?',' ')
		servicename = servicename.replace('{',' ')
		servicename = servicename.replace('}',' ')
		servicename = servicename.replace('(',' ')
		servicename = servicename.replace(')',' ')
		servicename = servicename.replace('[',' ')
		servicename = servicename.replace(']',' ')
		servicename = servicename.replace('^',' ')
		servicename = servicename.replace('+',' ')
		servicename = servicename.replace('|',' ')
		servicename = servicename.replace('-',' ')
		servicename = servicename.replace('_',' ')
		servicename = servicename.replace('"',' ')
		servicename = servicename.replace('\'',' ')
		servicename = servicename.replace('#',' ')
		servicename = servicename.replace(':',' ')
		servicename = servicename.replace('!',' ')
		servicename = servicename.replace('`',' ')
		servicename = servicename.replace('.',' ')
		servicename = servicename.replace('\n','')
		servicename = servicename.strip()


		return servicename
	
	def getAspectRatio(self):
		
		d = {2:"16:9",3:"4:3"}
		return self.lookup_replace('aspect ratio', d)

	def getStatus(self):
			if self.offline:
				return "Offline"
			else:
				return "Online"
	
	def getEbno(self):
	
			ebno = self.lookupstr('Eb / No')
			ebno = ebno.replace(' ', '')
			ebno = ebno.replace('"', '')
			try:
					final = ebno[0:len(ebno)-2]+"."+ebno[:2]+"dB"
			except:
					final = ""
			if len(ebno) <= 1:
					final = ""
			final = final.replace(' ', '')
			final = final.replace('"', '')
			return final

	def getPol(self):
		d = {1:"Y",2:"X"}
		return self.lookup_replace('polarisation', d)
	
	def getBissStatus(self):
		d = {1:"CLEAR",2:"BISS"}
		return self.lookup_replace('Biss Status', d)
	
	
	def getSat(self):
			if not self.sat_dict.has_key(self.getinSatSetupInputSelect()):
	
	
				req = "SELECT SAT1,SAT2,SAT3,SAT4 FROM equipment WHERE id = %i" % self.getId()
				res = gv.sql.qselect(req)
				res = res[0] #1 line
				for x in range(len(res)):
					self.sat_dict[x + 1] = res[x]
			try:
				return self.sat_dict[self.getinSatSetupInputSelect()]
			except KeyError:
				return ""
	def get_lo_offset(self):
		try:
			return self.lo_offset
		except:
			req = "SELECT lo_offset FROM equipment WHERE id = %i" % self.getId()
			try:
				res = gv.sql.qselect(req)
				res = int(res[0][0])
			except:
				res = 0
			self.lo_offset = res
			return self.lo_offset
	def getChannel(self):
	
	
		result = ""
		#print status[i][0]
		if float(self.getinSatSetupSatelliteFreq()) < 2000: #then it's lband
			satfreq =  float(self.getinSatSetupSatelliteFreq()) + float(self.get_lo_offset())
			# C band
			if satfreq < 0:
				satfreq = -satfreq
			satfreq = str(satfreq)
		else:
			satfreq = str(self.getinSatSetupSatelliteFreq())
		channel_request = "SELECT c.channel, c.modulationtype FROM channel_def c WHERE ((c.sat =\"" + self.getSat() + "\") AND (c.pol =\"" + self.getPol() + "\") AND (c.frequency LIKE \"" + satfreq.split(".")[0] + "%\") AND (c.symbolrate  LIKE \"" + self.getinSatSetupSymbolRate().split(".")[0] + "%\"))"
		#print channel_request
		result = gv.sql.qselect(channel_request)
		if(len(result) != 0 ):
		   channel = str(result[0][0]) 
		   modulation = str(result[0][1])
		   channel = channel[0:(len(channel)-3)]
		   #channel = str(status[i][0]) + " " + channel + "/"
		
		else:
			#     channel = str(status[i][6])
			channel = ""
			modulation = ""
		
		
		
		#print i + 1,
		#print " = ",
		#print channel + " " + modulation 
		#return "UPDATE status SET channel ='%s', modtype ='%s' WHERE id ='%i'" %(channel,modulation,self.getId())
		return "UPDATE status SET channel ='%s'WHERE id ='%i'" %(channel,self.getId())
			
	def getVResol(self):
		return self.lookupstr('video vertical resolution')
	
	def getFrameRate(self):
		#d = {"1":"Unknown","2":"25 Hz","3":"30 Hz","4":"50 Hz","5":"60 Hz","6":"29.97 Hz","7":"59.97 Hz"}
		d = {"1":"Unknown","2":"25Hz","3":"30Hz","4":"50Hz","5":"60Hz","6":"29.97Hz","7":"59.97Hz"}
		return self.lookup_replace('video frame rate', d)
	
	def getVState(self):
		d = {"1":"Running","2":"Stopped","3":"Errors"}
		return self.lookup_replace('video state', d)
	
	def getAsiOutEncrypted(self):
		d = {"1":"Disabled","2":"Encrypted","3":"Patrially Decrypted","4":"Decrypted" }
		return self.lookup_replace('asi output mode', d)
	
	def getinSatSetupModType(self):
		key = 'inSatModType'
		return self.lookupstr(key)

	def getinSatSetupRollOff(self):
		""" Overide for RX8200 """
		d = {"1":"0.20","2":"0.35","3":"0.20"}
		return self.lookup_replace('inSatSetupRollOff ', d)
		
	def getinSatSetupSymbolRate(self):
			""" Take SPS return KSPS """
			key = "inSatSetupSymbolRate"
			try:
				symbolRateFloat = float(self.lookupstr(key))
			except ValueError:
				symbolRateFloat = 0
			symbolRateFloat = (symbolRateFloat / 1000)
			finalsymrate = str(symbolRateFloat)
			##print finalsymrate
			if(finalsymrate[(len(finalsymrate)-2):] == ".0"):
					finalsymrate = finalsymrate[:(len(finalsymrate)-2)]
			return finalsymrate
	
	def getinSatSetupSatelliteFreq(self):
			""" Take KHz Return MHz """
			
			try:
				SatelliteFreqFloat = float(self.lookupstr('inSatSetupSatelliteFreq'))
			except ValueError: 
				SatelliteFreqFloat = 0
							
			SatelliteFreqFloat = (SatelliteFreqFloat / 1000)
			finalSatelliteFreq = str(SatelliteFreqFloat)
							##print finalsymrate
							# This code is to compensate for inconsistencies in the D2S frequency table where
							# sometimes we have .0 at the end sometimes we don't
							# services.py then uses LIKE ...% to get it to match
			if(finalSatelliteFreq[(len(finalSatelliteFreq)-2):] == ".0"):
					finalSatelliteFreq = finalSatelliteFreq[:(len(finalSatelliteFreq)-2)]
			return finalSatelliteFreq    
	
	def getinSatSetupFecRate(self):
		"""Return FEC rate. Normally Auto"""
		d = {"1":"0","2":"1/2","3":"2/3","4":"3/4","5":"5/6","6":"6/7","7":"7/8","8":"8/9","9":"Auto"}
		return self.lookup_replace('inSatSetupFecRate', d)
		
	def getinputTsBitrate(self):
		key = 'inputtsbitrate '
		return self.lookupstr(key)
		
	def getinSatSetupInputSelect(self):
		"""For TT1260 and RX1290"""
		key = 'inSatSetupInputSelect '
		try:
				return int(self.lookupstr(key)) -1 
		except: 
				#print "can't be int"
				#print self.lookupstr(key)
				return 1
		
		
	def getinput_selection(self):
		""" Sat or ASI Different on each type so should be overriden"""
		return "ASI"
		
	def getlockState(self):
		d = {"1":"Unknown","2":"Lock","3":"Unlock"}
		return self.lookup_replace('LockState', d)
			
	
	def set_offline(self):
			self.offline = True
			try:
				order = "UPDATE status SET status ='Offline' WHERE id ='%i';" %self.getId()
				result = gv.sql.qselect(order)
				order = "UPDATE equipment SET model_id ='OFFLINE' WHERE id ='%i';" %self.getId()
				result = gv.sql.qselect(order)
			except: pass
			
			
class GenericIRD(IRD):
	def __init__(self, equipmentId, ip, name):
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "GenericIRD"
		
		super( GenericIRD, self ).__init__()

	def updatesql(self):
		return "DO 0;" #DO NOTHING 
