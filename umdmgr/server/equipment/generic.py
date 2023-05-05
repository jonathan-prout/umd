from __future__ import division
from __future__ import print_function
from builtins import str
from builtins import range
from past.utils import old_div
from builtins import object

from helpers.logging import log
from server import gv

from helpers import alarm, httpcaller, snmp
from helpers import static_parameters

snmp.gv = gv  # in theory we don't want to import explictly the server's version of gv
import threading
import copy
import time
import re

import MySQLdb

class HTTPError(Exception):
	pass


class DBError(Exception):
	pass


class checkout(object):
	STAT_INIT = 0
	STAT_SLEEP = 1
	STAT_READY = 2
	STAT_INQUEUE = 3
	STAT_CHECKEDOUT = 4
	STAT_STUCK = 5

	def __getattribute__(self, x):
		if x in ["status", "jitter"]:
			with self.lock:
				return object.__getattribute__(self, x)
		else:
			return object.__getattribute__(self, x)

	def __setattribute__(self, x):
		if x in ["status", "jitter"]:
			with self.lock:
				return object.__setattribute__(self, x)
		else:
			return object.__setattribute__(self, x)

	def __init__(self, parent):
		self.parent = parent
		self.rlock = threading.RLock()
		self.lock = threading.Lock()
		self.status = checkout.STAT_INIT
		self.timestamp = time.time()
		self.jitter = 0

	def __enter__(self):
		self.rlock.acquire()
		self.status = checkout.STAT_CHECKEDOUT
		self.timestamp = time.time()

	def __exit__(self):
		self.status = checkout.STAT_SLEEP
		self.timestamp = time.time()
		self.rlock.release()

	def getStatus(self):
		if self.rlock.acquire(blocking=False):  # If locked then receiver should be checked out
			if self.status in [checkout.STAT_INIT, checkout.STAT_INQUEUE, checkout.STAT_READY, checkout.STAT_STUCK]:
				rval = int(self.status)
				self.rlock.release()
				return rval
			elif self.status == checkout.STAT_SLEEP:
				if time.time() > self.timestamp + self.parent.min_refresh_time():
					self.status = checkout.STAT_READY

				rval = int(self.status)
				self.rlock.release()
				return rval
			elif self.status == checkout.STAT_CHECKEDOUT:
				if time.time() > self.timestamp + 60:  # Checked out for 1 minute
					self.status = checkout.STAT_STUCK
				rval = int(self.status)
				self.rlock.release()
				return rval
			else:
				self.rlock.release()
				raise NotImplementedError("status %d" % self.status)  # should never happen
		else:
			if time.time() > self.timestamp + 60:  # Checked out for 1 minute
				self.status = checkout.STAT_STUCK
				rval = int(checkout.STAT_STUCK)
				return rval
			else:
				return int(checkout.STAT_CHECKEDOUT)

	def checkout(self):
		self.rlock.acquire()
		self.status = checkout.STAT_CHECKEDOUT
		self.timestamp = time.time()

	def checkin(self):
		self.status = checkout.STAT_SLEEP
		self.jitter = time.time() - self.timestamp
		self.timestamp = time.time()
		try:
			self.rlock.release()
		except RuntimeError:
			pass  # Error raised from releasing a non aquired lock error. Don't care.

	def enqueue(self):
		with self.rlock:
			self.status = checkout.STAT_INQUEUE
			self.timestamp = time.time()


class serializableObj(object):
	def __init__(self):
		self.seralisabledata = ["ip", "equipmentId", "name", "snmp_res_dict", "oid_get", "masked_oids",
							"oid_getBulk" "multicast_id_dict", "streamDict", "addressesbyname", "online", "modelType",
							"refreshType", "refreshCounter", "subequipment"]
	def serialize(self):
		"""serialize data without using pickle. Returns dict"""

		serial_data = {}
		
		for key in self.seralisabledata:
			if hasattr(self, key):
				serial_data[key] = copy.copy(getattr(self, key))
		return serial_data

	def deserialize(self, data):
		""" deserialise the data from above
		expected errors are KeyError (no modelType), Type Error (wrong model Type)"""
		if not data["modelType"] == self.modelType:
			raise TypeError("Tried to serialise data from %s into %s" % (data["modelType"], self.modelType))
		
		for key in self.seralisabledata:
			if key in data:
				if hasattr(self, key):
					setattr(self, key, None)
					setattr(self, key, copy.deepcopy(data[key]))
					del data[key]
		del data

	def __del__(self):
		for key in self.seralisabledata:
			setattr(self, key, None)
	
	def __repr__(self):
		return f"<{self.__class__.__name__} {self.name} {self.ip}>"

	def set_offline(self, excuse: str = "") -> None:
		if not self.offline:
			log("{}: Offline: {}".format(self.getId(), excuse), self, alarm.level.Major)
		self.offline = True

	def set_online(self, reason: str = "") -> None:
		if gv.loud and not self.offline and reason:
			log("{}: Online: {}".format(self.getId(), reason), self, alarm.level.Info)
		self.offline = False

class equipment(serializableObj):
	modelType = "Not Set"

	def __init__(self):
		super().__init__()
		self.oid_getBulk = {}
		self.oid_get = {}

	def getoid(self):
		""" Obtains SNMP Paramaters for ModelType according to database"""

		comsel = "SELECT model_param,model_command FROM model_command WHERE model_id = '%s' AND mode = 'GET'" % self.modelType
		comsel_bulk = "SELECT model_param,model_command FROM model_command WHERE model_id = '%s' AND mode = 'GETBULK'" % self.modelType

		try:
			snmp_command = gv.cachedSNMP(comsel)
			for i in range(len(snmp_command)):
				self.oid_get[snmp_command[i][0]] = snmp_command[i][1]
		except MySQLdb.Error:
			raise DBError('Get SNMP COMMANDS')
		try:
			snmp_command = gv.cachedSNMP(comsel_bulk)
			for i in range(len(snmp_command)):
				self.oid_getBulk[snmp_command[i][0]] = snmp_command[i][1]

		except MySQLdb.Error:
			raise DBError('Get SNMP BULK COMMANDS')

	# self.oid_get2 = self.oid_get #there is a bug that overwrites self.oid_get. I can't find it
	# gv.sql.close()

	def refresh(self):
		""" Refresh method of class """
		""" removed import snmp here """
		try:
			self.snmp_res_dict = snmp.get(self.getoids(), self.ip)

		except Exception: # NOQA PyBroadException
			self.set_offline()
		if len(list(self.snmp_res_dict.keys())) < len(list(self.getoids().keys())):
			self.oid_mask()

		if len(self.snmp_res_dict) == 0:
			self.set_offline()
		if len(self.oid_getBulk) != 0:
			self.snmp_res_dict.update(snmp.walk(self.bulkoids(), self.ip))

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
			return self.snmp_res_dict[key]
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
		# d = {'DeviceType':".1.3.6.1.4.1.1773.1.1.1.7.0"}
		equipTypes = [
			[
				{'DeviceType': ".1.3.6.1.4.1.27338.5.2.2.0"}
				, "testing whether it's an  Ateme",
				"DR5000"
			], [
				{'DeviceType': ".1.3.6.1.4.1.37576.2.3.1.5.1.2.1"}
				# This is not the best but then that is not on older versions of NS mib
				, "testing whether it's a  Novelsat",
				"NS2000"
			], [
				{'DeviceType': ".1.3.6.1.2.1.1.1.0"},  # sysdescr.0
				"testing whether it's a Tandberg or TVIPS",
				""
			]
		]

		""" Speed up assesment process """
		equipTypes_ateme_first = [equipTypes[0], equipTypes[1], equipTypes[2]]
		equipTypes_novelsat_first = [equipTypes[1], equipTypes[0], equipTypes[2]]
		equipTypes_sysdecr_first = [equipTypes[2], equipTypes[0], equipTypes[1]]
		SNMPFIRST = 0
		HTTPFIRST = 1
		testmap = [
			("RX8200", equipTypes_sysdecr_first, SNMPFIRST),
			("RX1290", equipTypes_sysdecr_first, SNMPFIRST),
			("TT1260", equipTypes_sysdecr_first, SNMPFIRST),
			("TVG420", equipTypes_sysdecr_first, SNMPFIRST),
			("DR5000", equipTypes_ateme_first, SNMPFIRST),
			("NS2000", equipTypes_novelsat_first, SNMPFIRST),
			("Titan", equipTypes_sysdecr_first, HTTPFIRST),
		]
		get_order = SNMPFIRST
		for name, test, order in testmap:
			if name in self.modelType.upper():
				equipTypes = test
				get_order = order
				break

		def type_test_snmp(equipTypes):
			for test, blurb, setType in equipTypes:
				ver_found = False
				try:
					resdict = snmp.get(test, self.ip)
					assert (resdict != {})
					if setType != "":
						resdict['DeviceType'] = setType

					self.offline = False

					ver_found = True
					return resdict, ver_found

				except Exception:
					pass

			if not ver_found:
				self.offline = True
				resdict = {'DeviceType': "OFFLINE"}
				ver_found = False
			return resdict, ver_found

		def type_test_http():
			try:
				response, stringfromserver = httpcaller.get(self.ip, '80', '/appliance/api/ping')
				if response['status'] != '200':
					raise HTTPError()
				self.online = True
				resdict = {'DeviceType': "Titan"}
				ver_found = True
				return resdict, ver_found
			
			except HTTPError:
				pass

				self.offline = True
				resdict = {'DeviceType': "OFFLINE"}
				ver_found = False

			return resdict, ver_found
		sysdesc = {'DeviceType': ".1.3.6.1.2.1.1.1.0"}  # sysdescr.0
		nov_soft_ver = {
			'DeviceType': ".1.3.6.1.4.1.37576.2.3.1.5.1.2.1"}  # This is not the best but then that is not on older versions of NS mib

		# resdict  = snmp.get({'DeviceType':".1.3.6.1.4.1.1773.1.1.1.7.0"}, self.ip)
		if get_order == HTTPFIRST:
			resdict, ver_found = type_test_http()
			if resdict.get("DeviceType", "OFFLINE") == "OFFLINE":
				resdict, ver_found = type_test_snmp(equipTypes)
			if 'DeviceType' in resdict:
				return resdict['DeviceType']
			else:
				if gv.loud:
					log(resdict, self, alarm.level.Warning)
				self.offline = True
				return "OFFLINE"
		else:
			resdict, ver_found = type_test_snmp(equipTypes)
			if resdict.get("DeviceType", "OFFLINE") == "OFFLINE":
				resdict, ver_found = type_test_http()
			if 'DeviceType' in resdict:
				return resdict['DeviceType']
			else:
				if gv.loud:
					log(resdict, self, alarm.level.Warning)
				self.offline = True
				return "OFFLINE"

	def determine_subtype(self):
		"""  Gets a unit's subtype if required. Override if the unit actually has a subtype"""
		try:
			return self.modelType
		except AttributeError:
			return "Unknown"



	def get_offline(self):
		try:
			return self.offline
		except AttributeError:
			return True

	def min_refresh_time(self):
		return gv.min_refresh_time


class IRD(equipment):
	def __init__(self):
		super(IRD, self).__init__()
		self.oid_get = {}
		self.getoid()
		self.snmp_res_dict = {}
		self.sat_dict = {}
		self.offline = False
		self.masked_oids = {}
		self.checkout = checkout(self)

	def oid_mask(self):
		try:
			masks = self.masked_oids[self.getinSatSetupInputSelect()]
		except KeyError:
			masks = []
		for key in list(self.oid_get.keys()):
			if key not in self.snmp_res_dict:
				if gv.loud:
					log("%s at %s returned no such name for %s so masking" % (self.modelType, self.ip, key),
						self, alarm.level.Info)
				masks.append(key)
		self.masked_oids[self.getinSatSetupInputSelect()] = masks

	def getoids(self):

		dic = self.oid_get.copy()
		try:
			masks = self.masked_oids[self.getinSatSetupInputSelect()]
		except KeyError:
			masks = []

		for k, v in list(dic.items()):
			v = v.replace('enterprises.', '.1.3.6.1.4.1.')
			v = v.replace('X', str(self.getinSatSetupInputSelect()))
			dic[k] = v
			try:
				if not self.getRefreshType(static_parameters.snmp_refresh_types[k]):
					del dic[k]
			except KeyError:
				pass
			if k in masks:
				try:
					del dic[k]
				except KeyError:
					pass


		return dic

	def bulkoids(self):
		dic = self.oid_getBulk.copy()
		for k in list(dic.keys()):
			try:
				if not self.getRefreshType(static_parameters.snmp_refresh_types[k]):
					del dic[k]
			except KeyError:
				pass
		return dic

	def getServiceName(self):
		try:
			serviceName = self.snmp_res_dict["service name"]
		except KeyError:
			serviceName = ""
		return self.processServiceName(serviceName)

	def processServiceName(self, servicename):
		servicename = servicename.strip()

		servicename = re.sub(r"[^\w\d\s]", "", servicename)
		# [ group
		#  ^ not
		#   \w word
		#   \d digit
		#    \s space

		servicename = servicename.strip()

		return servicename

	def getAspectRatio(self):

		d = {2: "16:9", 3: "4:3"}
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
			final = ebno[0:len(ebno) - 2] + "." + ebno[:2] + "dB"
		except (IndexError, TypeError):
			final = ""
		if len(ebno) <= 1:
			final = ""
		final = final.replace(' ', '')
		final = final.replace('"', '')
		return final

	def getPol(self):
		d = {1: "Y", 2: "X"}
		return self.lookup_replace('polarisation', d)

	def getBissStatus(self):
		d = {1: "CLEAR", 2: "BISS"}
		return self.lookup_replace('Biss Status', d)

	def getSat(self):
		if self.getinSatSetupInputSelect() not in self.sat_dict:

			try:
				req = "SELECT SAT1,SAT2,SAT3,SAT4 FROM equipment WHERE id = %i" % self.getId()
				res = gv.sql.qselect(req)
				res = res[0]  # 1 line
				for x in range(len(res)):
					self.sat_dict[x + 1] = res[x]
			except (IndexError, MySQLdb.Error):
				pass
		try:
			return self.sat_dict[self.getinSatSetupInputSelect()]
		except KeyError:
			return ""

	def get_lo_offset(self):
		try:
			return self.lo_offset
		except AttributeError:
			req = "SELECT lo_offset FROM equipment WHERE id = %i" % self.getId()
			try:
				res = gv.sql.qselect(req)
				res = int(res[0][0])
			except (IndexError):
				res = 0
			self.lo_offset = res
			return self.lo_offset

	def getChannel(self):


		if float(self.getinSatSetupSatelliteFreq()) < 2000:  # then it's lband
			satfreq = float(self.getinSatSetupSatelliteFreq()) + float(self.get_lo_offset())
			# C band
			if satfreq < 0:
				satfreq = -satfreq
			satfreq = str(satfreq)
		else:
			satfreq = str(self.getinSatSetupSatelliteFreq())
		channel_request = "SELECT c.channel, c.modulationtype FROM channel_def c WHERE ((c.sat =\"" + self.getSat() + "\") AND (c.pol =\"" + self.getPol() + "\") AND (c.frequency LIKE \"" + \
		                  satfreq.split(".")[0] + "%\") AND (c.symbolrate  LIKE \"" + \
		                  self.getinSatSetupSymbolRate().split(".")[0] + "%\"))"
		result = gv.cachedSNMP(channel_request)
		if (len(result) != 0):
			channel = str(result[0][0])
			modulation = str(result[0][1])
			channel = channel[0:(len(channel) - 3)]
		# channel = str(status[i][0]) + " " + channel + "/"

		else:
			#     channel = str(status[i][6])
			channel = ""
			modulation = ""


		return "UPDATE status SET channel ='%s'WHERE id ='%i'" % (channel, self.getId())

	def getVResol(self):
		return self.lookupstr('video vertical resolution')

	def getFrameRate(self):
		# d = {"1":"Unknown","2":"25 Hz","3":"30 Hz","4":"50 Hz","5":"60 Hz","6":"29.97 Hz","7":"59.97 Hz"}
		d = {"1": "Unknown", "2": "25Hz", "3": "30Hz", "4": "50Hz", "5": "60Hz", "6": "29.97Hz", "7": "59.97Hz"}
		return self.lookup_replace('video frame rate', d)

	def getVState(self):
		d = {"1": "Running", "2": "Stopped", "3": "Errors"}
		return self.lookup_replace('video state', d)

	def getAsiOutEncrypted(self):
		d = {"1": "Disabled", "2": "Encrypted", "3": "Patrially Decrypted", "4": "Decrypted"}
		return self.lookup_replace('asi output mode', d)

	def getinSatSetupModType(self):
		key = 'inSatModType'
		return self.lookupstr(key)

	def getinSatSetupRollOff(self):
		""" Overide for RX8200 """
		d = {"1": "0.20", "2": "0.35", "3": "0.20"}
		return self.lookup_replace('inSatSetupRollOff ', d)

	def getinSatSetupSymbolRate(self):
		""" Take SPS return KSPS """
		key = "inSatSetupSymbolRate"
		try:
			symbolRateFloat = float(self.lookupstr(key))
		except ValueError:
			symbolRateFloat = 0
		symbolRateFloat = (old_div(symbolRateFloat, 1000))
		finalsymrate = str(symbolRateFloat)

		if (finalsymrate[(len(finalsymrate) - 2):] == ".0"):
			finalsymrate = finalsymrate[:(len(finalsymrate) - 2)]
		return finalsymrate

	def getinSatSetupSatelliteFreq(self):
		""" Take KHz Return MHz """

		try:
			SatelliteFreqFloat = float(self.lookupstr('inSatSetupSatelliteFreq'))
		except ValueError:
			SatelliteFreqFloat = 0

		SatelliteFreqFloat = (old_div(SatelliteFreqFloat, 1000))
		finalSatelliteFreq = str(SatelliteFreqFloat)

		# This code is to compensate for inconsistencies in the D2S frequency table where
		# sometimes we have .0 at the end sometimes we don't
		# services.py then uses LIKE ...% to get it to match
		if (finalSatelliteFreq[(len(finalSatelliteFreq) - 2):] == ".0"):
			finalSatelliteFreq = finalSatelliteFreq[:(len(finalSatelliteFreq) - 2)]
		return finalSatelliteFreq

	def getinSatSetupFecRate(self):
		"""Return FEC rate. Normally Auto"""
		d = {"1": "0", "2": "1/2", "3": "2/3", "4": "3/4", "5": "5/6", "6": "6/7", "7": "7/8", "8": "8/9", "9": "Auto"}
		return self.lookup_replace('inSatSetupFecRate', d)

	def getinputTsBitrate(self):
		key = 'inputtsbitrate '
		return self.lookupstr(key)

	def getinSatSetupInputSelect(self) -> int:
		"""For TT1260 and RX1290"""
		key = 'inSatSetupInputSelect '
		try:
			return int(self.lookupstr(key)) - 1
		except (TypeError, ValueError):
			# print "can't be int"
			# print self.lookupstr(key)
			return 1

	def getinput_selection(self):
		""" Sat or ASI Different on each type so should be overriden"""
		return "ASI"

	def getlockState(self):
		d = {"1": "Unknown", "2": "Lock", "3": "Unlock"}
		return self.lookup_replace('LockState', d)

	def getServiceID(self):
		key = 'ServiceID'
		return self.lookupstr(key)

	def getNumServices(self):
		key = 'numServices'
		try:
			return int(self.lookup(key))
		except (TypeError, ValueError):
			return 0

	def set_offline(self, excuse: str = "") -> None:
		if not self.offline:
			log("{}: Offline: {}".format(self.getId(), excuse), self, alarm.level.Major)
		self.offline = True
		try:
			order = "UPDATE status SET status ='Offline' WHERE id ='%i';" % self.getId()
			result = gv.sql.qselect(order)
			order = "UPDATE equipment SET model_id ='OFFLINE' WHERE id ='%i';" % self.getId()
			result = gv.sql.qselect(order)
		except Exception as e:
			log("{}: error when trying to set offline {}".format(self.getId(), e), self, alarm.level.Critical)

	def set_online(self, excuse: str = "") -> None:
		if self.offline:
			log("{}: Online: {}".format(self.getId(), excuse), self, alarm.level.Info)
		self.offline = False
		try:
			order = "UPDATE status SET status ='Online' WHERE id ='%i';" % self.getId()
			result = gv.sql.qselect(order)
			order = "UPDATE equipment SET model_id ='%s' WHERE id ='%i';" % (self.determine_subtype(), self.getId())
			result = gv.sql.qselect(order)
		except Exception as e:
			log("{}: error when trying to set online {}".format(self.getId(), e), self, alarm.level.Critical)

	def getRefreshType(self, criteria):
		if not hasattr(self, "refreshType"):
			self.refreshType = "full"
		if not hasattr(self, "refreshCounter"):
			self.refreshCounter = 0
		if self.refreshCounter == 10:
			self.refreshCounter = 0
		if self.refreshCounter == 0:
			self.refreshType = "full"
		if self.refreshType == "full":
			return True
		if criteria == "all":
			return True
		if criteria in self.refreshType:
			return True
		return False

	def set_refreshType(self, newType):
		if newType.replace(" ", "") != "":
			self.refreshType = newType
		else:
			self.refreshType = "full"


class GenericIRD(IRD):
	def __init__(self, equipmentId, ip, name, subequipment = None):
		super(GenericIRD, self).__init__()
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.subequipment = subequipment
		self.modelType = "GenericIRD"



	def updatesql(self):
		return "DO 0;"  # DO NOTHING
