from plugin_omneon import OmneonHelper
import gv
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
		if set( self.addressesbyname.keys() ) != set( self.streamDict.keys() ) : #Only get recorders if really needed
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
		#response, stringfromserver = httpcaller.get(self.ip, '9980', "csvoutput?--login=auto")
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
	def min_refresh_time(self):
		return 60