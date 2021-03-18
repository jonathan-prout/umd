from __future__ import absolute_import
from builtins import range
from past.builtins import basestring
from .plugin_omneon import OmneonHelper
from server import gv
from helpers import httpcaller
from .generic import checkout
from . import generic


octShift = [24,16,8,0]
def ipv4equal(ip1, ip2):
	""" list of int for octets or string for ipv4 address
	'192.168.0.1' or [192,168,0,1]"""
	if not ip1:
		return False
	if not ip2:
		return False
	if isinstance(ip1, basestring):
		ip1 = [int(octet) for octet in ip1.split(".")]
	if isinstance(ip2, basestring):
		ip2 = [int(octet) for octet in ip2.split(".")] 
	for i in range(4):
		if ip1[i] != ip2[i]:
			return False
	return True
def ipv4toint(net):
	binNet = 0
	On = 0
	for o in net.split("."):
		binNet += int(o) << octShift[On]
		On += 1
	return binNet

def ismulticast(ipv4addrss):
	return ipv4toint(ipv4addrss) & (0b11110000<<24)  == ipv4toint("224.0.0.0")

class IPGridport(OmneonHelper, generic.serializableObj):
	def __init__(self, equipmentId, ip, name, *args, **kwargs):
		super(IPGridport, self).__init__()
		self.seralisabledata = ["ip", "equipmentId", "name", "online", "modelType", "activeStreams"
							"refreshType", "refreshCounter"]
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
			#self.addressesbyname = dict(zip(owners, multicastaddresses))
			self.addressesbyname = {}
			for i in range(len(owners)):
				try:
					if ismulticast(multicastaddresses[i]):
						self.addressesbyname[owners[i]] = multicastaddresses[i]
				except IndexError:
					break
		self.set_online()
		
	def updatesql(self):
		activeDict = {}
		l = []
		for key, val in list(self.multicast_id_dict.items()):
			activeDict[val] = 0
		for key in self.activeStreams:
			try:
				mca = self.addressesbyname[key]
			except KeyError:
				continue
			_id = self.multicast_id_dict.get(mca, None)
			if _id is not None:
				activeDict[_id] = 1
			else:
				for m in list(self.multicast_id_dict.keys()):
					if ipv4equal(mca, m):
						_id = self.multicast_id_dict[m]
						activeDict[_id] = 1
						break
		for key, val in list(activeDict.items()):
			if key is not None:
				line = "update `status` set `OmneonRec` = %s where `id` = %s" %(val, key)
				l.append(line)
		return "; ".join(l) + "; update `status` set `updated`= CURRENT_TIMESTAMP where `id` = %s;"%self.equipmentId
				
	def getChannel(self):
		return "DO 0;" #DO NOTHING 
	def getId(self):
		return self.equipmentId 

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
