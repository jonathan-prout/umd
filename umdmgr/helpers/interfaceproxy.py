import typing
import time

class DictKeyProxy(object):
	""" This class works like a Bagels datamodel interface object for setting and getting data while representing
	that data in a dictionary. This is so we can easily port drivers from Bagels to the UMD manager.
	"""
	def __init__(self, data: dict = {}):
		self.data = data


	def setKey(self, key, value):
		"""Function to set the data key """
		if any([self.getKey(key) != value, key not in self.data]):
			self.data[key] = {
				"value": value,
				"updated": time.time(),
				"changed": time.time()
			}
		else:
			self.data[key]["updated"] = time.time()

	def getKey(self, key, default: typing.Any = None):
		return self.data.get(key, {}).get("value", default)

	def getUpdated(self, key, default: int = 0):
		return self.data.get(key, {}).get("updated", default)

	def getChanged(self, key, default: int = 0):
		return self.data.get(key, {}).get("changed", default)

	def getInterface(self, name):
		"""Returns a DictKey Proxy with the name. This is stored as a key in the current DictKeyProxy
		"""
		ifname = f"interface-{name}"
		if ifname not in self.data:
			self.data[ifname] = {}
		return DictKeyProxy(self.data[ifname])
