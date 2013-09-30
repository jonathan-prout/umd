import gv
import plugin_tvips
from plugin_omneon import OmneonHelper


class equipment(object):
	def getoid(self):

		self.oid_get = {}
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
		import snmp
		try:
			self.snmp_res_dict  = snmp.get(self.getoids(), self.ip)
		except:
			self.offline = True
		if len(self.snmp_res_dict.keys()) < len(self.getoids().keys()):
			self.oid_mask()

		if len(self.snmp_res_dict) == 0:
			self.offline = True
		if len(self.oid_getBulk) !=0:
			self.snmp_res_dict.update( snmp.getnext(self.bulkoids(), self.ip) )
	def getId(self):
		return self.equipmentId       
	def oid_mask(self):
		pass

	def getoids(self):
		return self.oid_get
	def oid_get_function(self):
		return self.oid_get2
	def bulkoids(self):
		return self.oid_getBulk

	def lookup(self, key):
		try:
			return  self.snmp_res_dict[key]
		except KeyError:
			return ""
		
	def lookup_replace(self, key, d):
		try:
			r = self.snmp_res_dict[key]
		except KeyError:
			r = ""
		try:
			return d[r]
		except KeyError:
			return ""

	def determine_type(self):
		""" determine Type. Returns string and
		should be processed outside the class as the idea is to replace with the correct device class"""
		import snmp
		#d = {'DeviceType':".1.3.6.1.4.1.1773.1.1.1.7.0"}
		d = {'DeviceType':".1.3.6.1.2.1.1.1.0"} #sysdescr.0
		
		#resdict  = snmp.get({'DeviceType':".1.3.6.1.4.1.1773.1.1.1.7.0"}, self.ip)
		try:
			resdict  = snmp.get(d, self.ip)
			self.offline = False
		except:
			self.offline = True
			resdict = {'DeviceType':"OFFLINE"}
		if resdict.has_key('DeviceType'):
			return resdict['DeviceType']
		else:
			if gv.loud:
				print resdict
			self.offline = True
			return "OFFLINE"
	def set_offline(self):
	    self.offline = True
			
	def get_offline(self):
		try:
			return self.offline
		except:
			return True
			
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

        return servicename

    def getAspectRatio(self):
        if self.modelType == "RX8200":
            d = {"1":"16:9","2":"4:3"}
        else:
            d = {"2":"16:9","3":"4:3"}
        return self.lookup_replace('aspect ratio', d)
        
    def getStatus(self):
		if self.offline:
			return "Offline"
		else:
			return "Online"

    def getEbno(self):
  
		ebno = self.lookup('Eb / No')
		try:
				final = ebno[0:len(ebno)-2]+"."+ebno[:2]+"dB"
		except:
				final = ""
		if len(ebno) <= 1:
				final = ""
		return final
        
    def getPol(self):
        d = {"1":"Y","2":"X"}
        return self.lookup_replace('polarisation', d)

    def getBissStatus(self):
        d = {"1":"Off","2":"On"}
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
		
    def getChannel(self):


		result = ""
		#print status[i][0]
		channel_request = "SELECT c.channel, c.modulationtype FROM channel_def c WHERE ((c.sat =\"" + self.getSat() + "\") AND (c.pol =\"" + self.getPol() + "\") AND (c.frequency LIKE \"" + self.getinSatSetupSatelliteFreq() + "%\") AND (c.symbolrate  LIKE \"" + self.getinSatSetupSymbolRate() + "%\"))"
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
        return self.lookup('video vertical resolution')
    
    def getFrameRate(self):
        #d = {"1":"Unknown","2":"25 Hz","3":"30 Hz","4":"50 Hz","5":"60 Hz","6":"29.97 Hz","7":"59.97 Hz"}
	d = {"1":"Unknown","2":"25Hz","3":"30Hz","4":"50Hz","5":"60Hz","6":"29.97Hz","7":"59.97Hz"}
        return self.lookup_replace('video frame rate', d)

    def getVState(self):
        d = {"1":"Running","2":"Stopped","3":"Errors"}
        return self.lookup_replace('video state', d)
    
    def getAsioutMode(self):
        d = {"1":"Disabled","2":"Encrypted","3":"Patrially Decrypted","4":"Decrypted" }
        return self.lookup_replace('asi output mode', d)
    
    def getinSatSetupModType(self):
        key = 'inSatModType'
        return self.lookup(key)
		
    def getinSatSetupRollOff(self):
        """ Overide for RX8200 """
        d = {"1":"0.20","2":"0.35","3":"0.20"}
        return self.lookup_replace('inSatSetupRollOff ', d)
        
    def getinSatSetupSymbolRate(self):
		key = "inSatSetupSymbolRate"
		try:
			symbolRateFloat = float(self.lookup(key))
		except ValueError:
			symbolRateFloat = 0
		symbolRateFloat = (symbolRateFloat / 1000)
		finalsymrate = str(symbolRateFloat)
		##print finalsymrate
		if(finalsymrate[(len(finalsymrate)-2):] == ".0"):
				finalsymrate = finalsymrate[:(len(finalsymrate)-2)]
		return finalsymrate
    
    def getinSatSetupSatelliteFreq(self):
		try:
			SatelliteFreqFloat = float(self.lookup('inSatSetupSatelliteFreq'))
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
        return self.lookup(key)
        
    def getinSatSetupInputSelect(self):
        """For TT1260 and RX1290"""
        key = 'inSatSetupInputSelect '
        try:
			return int(self.lookup(key)) -1 
        except: 
			#print "can't be int"
			#print self.lookup(key)
			return 1
        
        
    def getinput_selection(self):
        """ Sat or ASI Different on each type so should be overriden"""
        return "ASI"
        
    def getlockState(self):
        d = {"1":"Unknown","2":"Lock","3":"Unlock"}
        return self.lookup_replace('LockState', d)
		

	
	
class GenericIRD(IRD):
	def __init__(self, equipmentId, ip, name):
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "GenericIRD"
		
		super( GenericIRD, self ).__init__()

	def updatesql(self):
		return "DO 0;" #DO NOTHING 
class TT1260(IRD):
    
    
    def __init__(self, equipmentId, ip, name):
	self.equipmentId = equipmentId
	self.ip = ip
	self.name = name
	self.modelType = "TT1260"
	super( TT1260, self ).__init__()
    
    def getinSatSetupModType(self):
	    key = 'inSatModType'
	    d = {"5":"DVB-S2","2":"DVB-S"}
	    return self.lookup_replace(key, d)
    """ Done in IRD class
    def getoids(self):
        
	dic =  self.oid_get.copy()
	if self.getinSatSetupInputSelect() == 5:
	    for k, v in dic.items():
		if "X" in v:
		    del dic[k]
        
	for k, v in dic.items():
	    v = v.replace('enterprises.','.1.3.6.1.4.1.')
	    v = v.replace('X', str(self.getinSatSetupInputSelect()))
	    dic[k] = v
	#if self.getinSatSetupInputSelect() = 1:
	#    print "%s is on imput %s"%(self.name, self.getinSatSetupInputSelect())
        return dic
    """
    def updatesql(self):
        return  "UPDATE status SET status = '%s' , servicename = '%s', aspectratio ='%s', ebno='%s', pol='%s', bissstatus='%s', videoresolution='%s', framerate='%s',videostate='%s',asioutmode='%s',frequency='%s',symbolrate='%s',fec='%s',rolloff='%s',modulationtype='%s',muxbitrate='%s',muxstate='%s', asi='%s', sat_input='%i' WHERE id = %i; " %(self.getStatus(),self.getServiceName(),self.getAspectRatio(),self.getEbno(),self.getPol(),self.getBissStatus(),self.getVResol(),self.getFrameRate(),self.getVState(),self.getAsioutMode(),self.getinSatSetupSatelliteFreq(),self.getinSatSetupSymbolRate(),self.getinSatSetupFecRate(),self.getinSatSetupRollOff(),self.getinSatSetupModType(),self.getinputTsBitrate(),self.getlockState(),self.getinput_selection(),self.getinSatSetupInputSelect(),self.getId())

    def getinput_selection(self):
        """ Sat or ASI Different on each"""
        if self.getinSatSetupSatelliteFreq() == "0":
            return "ASI"
        else:
            return "SAT"
class RX1290(IRD):
    
    def __init__(self, equipmentId, ip, name):
        
        self.equipmentId = equipmentId
        self.ip = ip
        self.name = name
        self.modelType = "RX1290"
        super( RX1290, self ).__init__()
     
    def updatesql(self):
        return  "UPDATE status SET status = '%s' , servicename = '%s', aspectratio ='%s', ebno='%s', pol='%s', bissstatus='%s', videoresolution='%s', framerate='%s',videostate='%s',asioutmode='%s',frequency='%s',symbolrate='%s',fec='%s',rolloff='%s',modulationtype='%s',asi='%s',muxbitrate='%s', sat_input='%i' WHERE id = %i; " %(self.getStatus(),self.getServiceName(),self.getAspectRatio(),self.getEbno(),self.getPol(),self.getBissStatus(),self.getVResol(),self.getFrameRate(),self.getVState(),self.getAsioutMode(),self.getinSatSetupSatelliteFreq(),self.getinSatSetupSymbolRate(),self.getinSatSetupFecRate(),self.getinSatSetupRollOff(),self.getinSatSetupModType(),self.getinput_selection(),self.getinputTsBitrate(),self.getinSatSetupInputSelect(),self.getId())
    def getinSatSetupModType(self):
	    key = 'inSatModType'
	    d = {"2":"DVB-S2","1":"DVB-S"}
	    return self.lookup_replace(key, d)

    def getinput_selection(self):
        d = {"1":"ASI","2":"SAT"}
        return self.lookup_replace('input_selection ', d)
        
class RX8200(IRD):
    
    def __init__(self, equipmentId, ip, name):
        self.equipmentId = equipmentId
        self.ip = ip
        self.name = name
        self.modelType = "RX8200"
        super( RX8200, self ).__init__()
    def getlockState(self):
        d = {"1":"Lock","0":"Unlock"}
        return self.lookup_replace('LockState', d)

    def getinputTsBitrate(self):
	key = 'inputtsbitrate '
	s = self.lookup(key) + "000" #kbps to bps
	return s

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

    def getinSatSetupModType(self):
	    key = 'inSatModType'
	    d = {"1":"DVB-S2","0":"DVB-S"}
	    return self.lookup_replace(key, d)
   
    def getinSatSetupInputSelect(self):
		"""For RX8200
		# {channel_1(0),channel_2(1), channel_3(2), channel_4(3), channel_5(4), channel_6(5), channel_7(6), channel_8(7)}"""
		key = 'inSatSetupInputSelect '
		inp = self.lookup(key)
		try:
			return int(inp) +1   
		except ValueError:
			return 1
    def getinSatSetupRollOff(self):
        """for RX8200 """
        d = {"0":"0.20","1":"0.35","2":"0.20"}
        return self.lookup_replace('inSatSetupRollOff ', d)    

    def getinSatSetupFecRate(self):
	    """Return FEC rate. Normally Auto"""
	    #{auto(0), fec_1_2(102), fec_1_3(103), fec_1_4(104),fec_2_3(203),fec_2_5(205),fec_3_4(304), fec_3_5(305),fec_4_5(405), fec_5_6(506), fec_6_7(607), fec_7_8(708),fec_8_9(809), fec_9_10(910),fec_unknown(999)  
	    d = {"999":"0","102":"1/2","103":"1/3",     "104":"1/4",     "203":"2/3", "205":"2/5",   "304":"3/4",  "305":"3/5",   "405":"4/5",       "506":"5/6",  "607":"6/7",  "708":"7/8",   "809":"8/9",    "910":"9/10",  "0":"Auto"}
	    return self.lookup_replace('inSatSetupFecRate', d) 

    def getinput_selection(self):
	    d = {"0":"ASI","1":"SAT","2":"SAT"}
	    return self.lookup_replace('input_selection ', d)
    
    def getServiceName(self):
        try:
            Table_Service_ID = self.snmp_res_dict["Table_Service_ID"]
	    Table_Service_Name = self.snmp_res_dict["Table_Service_Name"]
	    ServiceID = self.snmp_res_dict["ServiceID"]
        except KeyError:
            return  ""
	for x in xrange(len(Table_Service_ID)):
	    try:
		Table_Service_ID[x] = int(Table_Service_ID[x])
	    except ValueError:
		Table_Service_ID[x] = -1
	try:
	    pos = Table_Service_ID.index(int(ServiceID))
	    serviceName = Table_Service_Name[pos]
	    return self.processServiceName(serviceName)
	except:
	    return ""

    def getEbno(self):
  
		ebno = self.lookup('Eb / No')
		try:
				final = ebno.replace(" ", "")
				final = ebno.replace("+", "")
		except:
				final = ""
		if len(ebno) <= 1:
				final = ""
		return final
	
    def getPol(self):
        d = {"0":"Y","1":"X"}
        return self.lookup_replace('polarisation', d)
	
    def getBissStatus(self):
        d = {"0":"Off","1":"On"}
        return self.lookup_replace('Biss Status', d)
    def getFrameRate(self):
        #d = {"1":"Unknown","2":"25Hz","3":"30Hz","4":"50Hz","5":"60Hz","6":"29.97Hz","7":"59.97Hz"}
        fr = self.lookup('video frame rate')
	try:
	    fr = float(fr)
	except:
	    fr = 0
	fr = fr/1000
	st = "%sHz"% fr
	st = st.replace(".0", "")
	return st

class oidWorkaround(equipment):
     def __init__(self, modelType):
	self.modelType = modelType
	self.getoid()


	
class TVG420(plugin_tvips.TVG420):
	def __init__(self, equipmentId, ip, name):
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "TVG420"
		super( TVG420, self ).__init__(self.ip, "admin", "salvador")
		self.get_equipment_ids()
		
		
	def get_offline(self):
		try:
			return  not self.online
		except:
			return True
	def set_offline(self):
	    self.online = False
	    
	def refresh(self):
		self.get_enable_only()
	
	def get_equipment_ids(self):
		self.multicast_id_dict = {}
		comsel = "SELECT `equipment`.`id`, `equipment`.`MulticastIp` FROM equipment"

		sql_res = gv.sql.qselect(comsel)
		for item in sql_res:
			self.multicast_id_dict[item[1]] = int(item[0])
		
	def updatesql(self):
		l = []
		b = {"true":1,"false":0}
		d = self.usage_by_addr()
		for k in d.keys():
			try:
				line = "update `status` set `TvipsRec` = %s where `id` = %s" %( b[d[k]], self.multicast_id_dict[k])
				l.append(line)
			except KeyError:
				pass
		return "" + "; ".join(l) + ";"
		
	def getChannel(self):
		return "DO 0;" #DO NOTHING 
	def getId(self):
		return self.equipmentId 
			
class IPGridport(OmneonHelper):
	def __init__(self, equipmentId, ip, name):
		import httpcaller
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "IP GRIDPORT"
		self.addressesbyname = {}
		self.get_equipment_ids()
		self.offline = False
		
	def get_equipment_ids(self):
	
		self.multicast_id_dict = {}
		comsel = "SELECT `equipment`.`id`, `equipment`.`MulticastIp` FROM equipment"

		sql_res = gv.sql.qselect(comsel)
		for item in sql_res:
			self.multicast_id_dict[item[1]] = int(item[0])		
			
			
	def refresh(self):
		self.streamDict = self.getrecorders(returnlist="dict") #Refresh list of streams
		if set( self.addressesbyname.keys() ).issubset( set( self.streamDict.keys() ) ): #Only get recorders if really needed
			owners, ports, multicastaddresses = self.getports()
			self.addressesbyname = dict(zip(owners, multicastaddresses))
		
	def updatesql(self):
		activeDict = {}
		l = []
		for key, val in self.multicast_id_dict.items():
			activeDict[val] = 0
		for key in self.streamDict.keys():
			try:
				mca = self.addressesbyname[key]
				id = self.multicast_id_dict[mca]
				activeDict[id] = 1
			except KeyError:
				pass
		for key, val in activeDict.items():
			line = "update `status` set `OmneonRec` = %s where `id` = %s" %(val, key)
			l.append(line)
		return "; ".join(l) + ";"
				
	def getChannel(self):
		return "DO 0;" #DO NOTHING 
	def getId(self):
		return self.equipmentId 
			
	def get_offline(self):
		return self.offline
	def set_offline(self):
	    self.offline = True
	    
	def determine_type(self):
		import httpcaller
		response, stringfromserver = httpcaller.get(self.ip, '9980', "csvoutput?--login=auto")
		try:
			response, stringfromserver = httpcaller.get(self.ip, '9980', "csvoutput?--login=auto")
		except:
			
			response = {'status':'500'}
		if response['status'] != '200': 
			#die( zip(response, "----------", "Bad response from server when getting streamstores from ", ipgridportiplist[item]))
			self.offline = True
		else:
			self.offline = False
		return "IP Gridport"