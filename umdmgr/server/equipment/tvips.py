from __future__ import absolute_import
from builtins import range
import copy
from . import plugin_tvips
from server import gv
from .generic import checkout, equipment


class TVG420(plugin_tvips.TVG420, equipment):
	def __init__(self, equipmentId, ip, name, *args, **kwargs):
		super(TVG420, self).__init__(equipmentId, ip, name)
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "TVG420"
		self.username = "admin"
		self.password = "password"
		self.ports = []
		self.get_equipment_ids()
		self.checkout = checkout(self)
		self.online = True
		self.seralisabledata = ["ip", "equipmentId", "name", "online", "modelType", "refreshType", "refreshCounter",
								"enablelist", "labellist", "dirlist", "destlist", "ids", "ip_tx_rate", "ip_rx_rate",
								"multicast_id_dict"]

	def serialize(self):
		"""serialize data without using pickle. Returns dict"""

		serial_data = {}
		for key in self.seralisabledata:
			if hasattr(self, key):
				serial_data[key] = copy.copy(getattr(self, key))
		for i in range(len(self.ports)):
			serial_data["port-%d" % i] = self.ports[i].getData()

		return serial_data

	def deserialize(self, data):
		""" deserialise the data from above
		expected errors are KeyError (no modelType), Type Error (wrong model Type)"""
		if not data["modelType"] == self.modelType:
			raise TypeError("Tried to serialise data from %s into %s" % (data["modelType"], self.modelType))
		ports = {}
		for key in self.seralisabledata:
			if key in data:
				setattr(self, key, data[key])
		for key in list(data.keys()):
			if "port-" in key:
				try:
					ports[int(key.replace("port-", ""))] = data[key]
				except ValueError:
					continue
		self.ports = []
		for key in sorted(ports):
			self.ports.append(plugin_tvips.asiport(ports[key]))

	def get_offline(self):
		try:
			return not self.online
		except AttributeError:
			return True

	def set_offline(self, excuse: str = ""):
		if not self.offline:
			print("{}: Offline: {}".format(self.getId(), excuse))
		self.online = False

	def refresh(self):

		if not self.ports:
			self.get_port_config()

		self.get_enable_only()

	def get_equipment_ids(self):
		self.multicast_id_dict = {}
		comsel = "SELECT `equipment`.`id`, `equipment`.`MulticastIp` FROM equipment"

		sql_res = gv.cachedSNMP(comsel)
		for item in sql_res:
			self.multicast_id_dict[item[1]] = int(item[0])

	def updatesql(self):
		l = []
		b = {"true": 1, "false": 0}
		d = self.usage_by_addr()
		for k in list(d.keys()):
			try:
				line = "update `status` set `TvipsRec` = %s where `id` = %s" % (b[d[k]], self.multicast_id_dict[k])
				l.append(line)
			except KeyError:
				pass
		return "" + "; ".join(
			l) + ";update `status` set `updated`= CURRENT_TIMESTAMP where `id` = %s;" % self.equipmentId

	def getChannel(self):
		return "DO 0;"  # DO NOTHING

	def getId(self):
		return self.equipmentId

	def min_refresh_time(self):
		return 10
