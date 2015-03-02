import plugin_tvips
from server import gv
from generic import checkout, serializableObj

class TVG420(plugin_tvips.TVG420, serializableObj):
	def __init__(self, equipmentId, ip, name):
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "TVG420"
		super( TVG420, self ).__init__(self.ip, "admin", "salvador")
		self.get_equipment_ids()
		self.checkout = checkout(self)
	def serialize(self ):
		"""serialize data without using pickle. Returns dict"""
		
		serial_data = {}
		seralisabledata = ["ip", "equipmentId", "name", "online",  "modelType", "refreshType", "refreshCounter", "enablelist", "labellist","dirlist", "destlist", "ids", "ip_tx_rate","ip_rx_rate", "multicast_id_dict"]
		for key in seralisabledata:
			if hasattr(self, key):
				serial_data[key] = copy.copy(getattr(self, key))
					
		return serial_data
		
	def deserialize(self, data):
		""" deserialise the data from above
		expected errors are KeyError (no modelType), Type Error (wrong model Type)"""
		if not data["modelType"] == self.modelType:
			raise TypeError("Tried to serialise data from %s into %s"%(data["modelType"],self.modelType))
		seralisabledata = ["ip", "equipmentId", "name", "online",  "modelType", "refreshType", "refreshCounter", "enablelist", "labellist","dirlist", "destlist", "ids", "ip_tx_rate","ip_rx_rate", "multicast_id_dict"]
		for key in seralisabledata:
				if hasattr(self, key):
					setattr(self, key, data[key])	
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
		return "" + "; ".join(l) + ";update `status` set `updated`= CURRENT_TIMESTAMP where `id` = %s;"%self.equipmentId
		
	def getChannel(self):
		return "DO 0;" #DO NOTHING 
	def getId(self):
		return self.equipmentId 
	def min_refresh_time(self):
		return 10
	
