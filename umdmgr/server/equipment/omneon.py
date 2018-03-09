from plugin_omneon import OmneonHelper
from server import gv
from helpers import httpcaller
from generic import checkout
import generic
def ipv4equal(ip1, ip2):
	""" list of int for octets or string for ipv4 address
	'192.168.0.1' or [192,168,0,1]"""
	if isinstance(ip1, basestring):
		ip1 = [int(octet) for octet in ip1.split(".")]
	if isinstance(ip2, basestring):
		ip2 = [int(octet) for octet in ip2.split(".")] 
	for i in range(4):
		if ip1[i] != ip2[i]:
			return False
	return True

class IPGridport(OmneonHelper, generic.serializableObj):
	def __init__(self, equipmentId, ip, name):
		
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "IP GRIDPORT"
		self.addressesbyname = {}
		self.activeStreams = []
		self.get_equipment_ids()
		self.offline = False
		self.checkout = checkout(self)
			
			
	def get_equipment_ids(self):
	
		self.multicast_id_dict = {}
		comsel = "SELECT `equipment`.`id`, `equipment`.`MulticastIp` FROM equipment"

		sql_res = gv.sql.qselect(comsel)
		for item in sql_res:
			self.multicast_id_dict[item[1]] = int(item[0])		
			
			
	def refresh(self):
		self.get_equipment_ids() #Dynamically update to db changes
		self.activeStreams = self.getrecorders(returnlist="namesonly") #Refresh list of streams
		if set( self.activeStreams ) != set( self.addressesbyname.keys() ) : #Only get recorders if really needed
			owners, ports, multicastaddresses = self.getports()
			self.addressesbyname = dict(zip(owners, multicastaddresses))
		self.set_online()
		
	def updatesql(self):
		activeDict = {}
		l = []
		for key, val in self.multicast_id_dict.items():
			activeDict[val] = 0
		for key in self.activeStreams:
			try:
				mca = self.addressesbyname[key]
			except KeyError:
				continue
			_id = self.multicast_id_dict.get(mca, None)
			if id is not None:
				activeDict[_id] = 1
			else:
				for m in multicast_id_dict.keys():
					if ipv4equal(key, m):
						_id = self.multicast_id_dict[m]
						activeDict[_id] = 1
						break
		for key, val in activeDict.items():
			line = "update `status` set `OmneonRec` = %s where `id` = %s" %(val, key)
			l.append(line)
		return "; ".join(l) + "; update `status` set `updated`= CURRENT_TIMESTAMP where `id` = %s;"%self.equipmentId
				
	def getChannel(self):
		return "DO 0;" #DO NOTHING 
	def getId(self):
		return self.equipmentId 
	def set_online(self):
		self.offline = False			
	def get_offline(self):
		
		#import httpcaller
		#response, stringfromserver = httpcaller.get(self.ip, '9980', "csvoutput?--login=auto")
		try:
			response, stringfromserver = httpcaller.get(self.ip, self.port, "api/2/list/nodes/rec")
		except:
			
			response = {'status':'500'}
		if response['status'] != '200': 
			#die( zip(response, "----------", "Bad response from server when getting streamstores from ", ipgridportiplist[item]))
			self.offline = True
		else:
			self.offline = False
		return self.offline
	def set_offline(self):
		self.offline = True
		
	def determine_type(self):
		#import httpcaller
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
