import plugin_tvips
from server import gv

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
		return "" + "; ".join(l) + ";update `status` set `updated`= CURRENT_TIMESTAMP where `id` = %s;"%self.equipmentId
		
	def getChannel(self):
		return "DO 0;" #DO NOTHING 
	def getId(self):
		return self.equipmentId 
	def min_refresh_time(self):
		return 10
	
