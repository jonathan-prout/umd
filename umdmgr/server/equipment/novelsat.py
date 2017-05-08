from generic import IRD, GenericIRD
from server import gv
from helpers import snmp
snmp.gv = gv #in theory we don't want to import explictly the server's version of gv
class NS2000(IRD):
	def __init__(self, equipmentId, ip, name):
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "NS2000"
		super( NS2000, self ).__init__()
	
	
	def determine_type(self):
		return "NS2000"
	def determine_subtype(self):
		""" determines sub type of equipment
		"""
		""" removed import snmp here"""
		nov_soft_ver = {'ver': ".1.3.6.1.4.1.37576.2.3.1.5.1.5.1"} #nsCommonSystemSwVersionAppNsmd

		try:
			resdict  = snmp.get(nov_soft_ver, self.ip) 
			self.offline = False
			
		except:
			self.offline = True
			resdict = {'ver':"0.0"}
		if resdict.has_key("ver"): #well it ought to
			#NS2000.5.7.0.1949 07-Dec-2016 19:44
			ver = resdict["ver"].strip().split(" ")[0]
			ver = ver.replace('"', '')
			i = 0
			v = 0.0
			for rev in ver.split("."):
				try:
					v += int(rev)
					
				except:
					continue
			v = float("%d.%s"%(v[0], "".join("%d"%i for i in v[1:])))
			if gv.loud: print("Novelsat NS2000 version %s"%v)
			if v < 2.3:
				return "NS2000_WEB"
			else:
				return "NS2000_SNMP"
	def updatesql(self):
		sql =  "UPDATE status SET status = '%s' , "% self.getStatus()


		sql += "ebno='%s', "% self.getEbno()
		sql += "pol='%s', "% self.getPol()





		sql += "frequency='%s',"% self.getinSatSetupSatelliteFreq()
		sql += "symbolrate='%s',"% self.getinSatSetupSymbolRate()
		sql += "fec='%s',"% self.getinSatSetupFecRate()
		sql += "rolloff='%s',"% self.getinSatSetupRollOff()
		sql += "modulationtype='%s',"% self.getinSatSetupModType()
		sql += "updated= CURRENT_TIMESTAMP ,"
		sql += "muxbitrate='%s', "% self.getinputTsBitrate()
		sql += "muxstate='%s' "% self.getlockState()

		sql += "WHERE id = %i; " %self.getId()
		return sql
	
	def getinSatSetupInputSelect(self):
		return 1 #There's only one input
	def getPol(self):
		d = {"0":"?","1":"Y","2":"Y","3":"X","4":"X"}
		return self.lookup_replace('polarisation', d)
class NS2000_WEB(NS2000):
	def __init__(self, equipmentId, ip, name):
		super( NS2000_WEB, self ).__init__(equipmentId, ip, name)
		self.modelType = "NS2000_WEB"
	
	def refresh(self):
		""" refresh by HTTP"""
		
		
		#url = "http://10.73.238.113/query.fcgi?form_state=3&form_name=line_status&line_state=1"
		"""query.fcgi?form_state=1&form_name=line_demod"""
		status_keys = [{
			"inSatModType_actual":16
			,"sync":17
			,"ebno":18
			,"symbolrate":21
			,"rolloff":23
			,"freq":24
			,"datarate":26
			,"margin":27
			,"lock":28
			,"constellation":30
			,"fec":31
			,"pilot":32
			,"framesize":33
		},{
			"inSatModType_set":21
			,"Dual Channel":23
			,"rolloff_set":37
			,"golden seq":41
			,"polarisation":45
		}]
		
		
		
		import httpcaller
		page = ["query.fcgi?form_state=3&form_name=line_status&line_state=1", "query.fcgi?form_state=1&form_name=line_demod"]
		for i in range(2):
			try:
				response, stringfromserver = httpcaller.get(self.ip, '80', page[i])
			except:
				
				response = {'status':'500'}
			if response['status'] != '200': 
				self.set_offline()
			
			
			for errorcon in ["error", "wait"]:
				if errorcon in response:
					return #skip if in error
			res =  stringfromserver.split(";")
			if len(res) < 33:
				self.set_offline()
			
			for key in status_keys[i].keys():
				try:
					self.snmp_res_dict[key] = res[status_keys[i][key]]
				except IndexError:
					pass
	
		
	
	
	def getinSatSetupFecRate(self):
		return self.lookupstr('fec')
	
	def getinSatSetupRollOff(self):
		if self.getlockState() == "Lock":
			return self.lookupstr('rolloff')
		else:
			d = {'1': '0.10', '0': '0.05', '3': '0.20', '2': '0.15', '5': '0.35', '4': '0.25'}
			return self.lookup_replace('rolloff_set', d)

	
	def getEbno(self):
	
			ebno = self.lookupstr('margin')

			ebno = ebno.replace(' ', '')
			ebno = ebno.replace('"', '')
			return ebno
	def getlockState(self):
		#d = {"1":"Lock","0":"Unlock"}
		#return self.lookup_replace('LockState', d)
		d = {"Locked":"Lock","Unlocked":"Unlock"} # yes i know it's silly but ought to match
		return self.lookup_replace('lock', d)
	
	def getinputTsBitrate(self):
		key = 'datarate'
		val =  self.lookupstr(key)
		val = val.replace(" Mbit/Sec", "")
		val = val.strip()
		try:
			val = float(val)
		except:
			val = 0
		val = val * 1000000 #mbps -> bps
		return str( int( val )) #string of integer
	def getinSatSetupSatelliteFreq(self):
		key = 'freq'
		val =  self.lookupstr(key)
		val = val.replace(" MHz", "")
		val = val.strip()
		try:
			val = float(val)
		except:
			val = 0
		#val = val * 1 #Already MHZ. Note this is the Lband freq
		return str(  val ) #string of integer
	def getinSatSetupSymbolRate(self):
		val = self.lookupstr("symbolrate")
		val = val.replace(" MSPS", "")
		val = val.strip()
		try:
			val = float(val)
		except:
			val = 0
		val = val * 1000 #msps -> ksps
		return str( int( val )) #string of integer
	
	def getinSatSetupModType(self):
		if self.getlockState() == "Lock":
			return self.lookupstr('inSatModType_actual')
		else:
			d = {'1': 'DSNG', '0': 'DVB-S', '3': 'NS3', '2': 'DVB-S2'}
			return self.lookup_replace('inSatModType_set', d)
		

class NS2000_SNMP(NS2000):
	def __init__(self, equipmentId, ip, name):
		super( NS2000_SNMP, self ).__init__(equipmentId, ip, name)
		self.modelType = "NS2000_SNMP"
	def getinSatSetupSatelliteFreq(self):
		""" Take Hz Return MHz """
		
		try:
			SatelliteFreqFloat = float(self.lookupstr('inSatSetupSatelliteFreq'))
		except ValueError: 
			SatelliteFreqFloat = 0
						
		SatelliteFreqFloat = (SatelliteFreqFloat / 100000)
		finalSatelliteFreq = str(SatelliteFreqFloat)
						##print finalsymrate
						# This code is to compensate for inconsistencies in the D2S frequency table where
						# sometimes we have .0 at the end sometimes we don't
						# services.py then uses LIKE ...% to get it to match
		if(finalSatelliteFreq[(len(finalSatelliteFreq)-2):] == ".0"):
				finalSatelliteFreq = finalSatelliteFreq[:(len(finalSatelliteFreq)-2)]
		return finalSatelliteFreq
	def getinSatSetupFecRate(self):
		"""Return FEC rate."""
		d = {'24': '4/5Short', '25': '37/45', '26': '5/6', '27': '5/6Short',
			'20': '3/4', '21': '3/4Short','22': '7/9', '23': '4/5',
			'28': '7/8', '29': '8/9', '1': '1/4','0': '1/5', '3': '1/3',
			'2': '1/4Short', '5': '13/30', '4': '2/5', '7': '7/15','6': '4/9',
			'9': '1/2', '8': '22/45', '11': '8/15', '10': '1/2Short', '13': '17/30',
			'12': '5/9', '15': '28/45', '14': '3/5', '17': '2/3', '16': '19/30',
			'19':'11/15', '18': '32/45', '255': 'notApplicable', '30': '9/10'
			}
		return self.lookup_replace('inSatSetupFecRate', d)
	def getinSatSetupRollOff(self):
		""" NS2K SNMP """
		d = {'1': '0.10', '0': '0.05', '3': '0.20', '2': '0.15', '5': '0.35', '4': '0.25', '255': 'notApplicable'}
		return self.lookup_replace('inSatSetupRollOff', d)
	
	def getinSatSetupModType(self):
		d = {'1': 'DSNG', '0': 'DVB-S', '3': 'NS3', '2': 'DVB-S2'}
		return self.lookup_replace('inSatModType', d)
	def getlockState(self):
		d = {"1":"Lock","0":"Unlock"}
		return self.lookup_replace('LockState', d)
	