from __future__ import division
from __future__ import absolute_import
from builtins import str
from builtins import zip
from builtins import range
from past.utils import old_div
from server.equipment.generic import IRD, GenericIRD
from server import gv
from helpers import snmp


class DR5000(IRD):
	""" ATEME DR5000 version 1.0.2.2 """

	def __init__(self, equipmentId, ip, name):
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "DR5000"
		super(DR5000, self).__init__()

	def getAspectRatio(self):
		d = {1: "16:9", 2: "4:3"}
		return self.lookup_replace('aspect ratio', d)

	def getServiceName(self):
		try:
			Table_Service_ID = list(self.snmp_res_dict["Table_Service_ID"])
			Table_Service_Name = list(self.snmp_res_dict["Table_Service_Name"])
			ServiceID = self.getServiceId()
		except KeyError:
			return ""
		for x in range(len(Table_Service_ID)):
			try:
				Table_Service_ID[x] = int(Table_Service_ID[x])
			except ValueError:
				try:
					v = Table_Service_ID[x]
					v = v.replace('"', '')
					v = v.replace('\n', '')
					v = v.replace(' ', '')
					Table_Service_ID[x] = int(v)
				except ValueError:
					Table_Service_ID[x] = -1
		try:

			d = dict(list(zip(Table_Service_ID, Table_Service_Name)))

			serviceName = d[ServiceID]
			return self.processServiceName(serviceName)
		except:
			return ""

	def getServiceId(self):
		try:
			return int(self.lookupstr('ServiceID'))
		except ValueError:
			return 0

	def getEbno(self):
		""" 0 = unlock
		164 = 16.4db """
		ebno = self.lookupstr('Eb / No')
		try:
			ebno = float(ebno) / 10
		except ValueError:
			ebno = 0.0
		val = "%.1fdB" % ebno
		return str(val)

	def getPol(self):
		d = {"1": "Y", "2": "X"}
		return self.lookup_replace('polarisation', d)

	def getCAType(self):
		if not self.getCAStatus():
			return "CLEAR"
		try:
			index = self.snmp_res_dict["Table_Service_ID"].index(self.getServiceId())
		except ValueError:
			return "Service Missing"
		try:
			return self.snmp_res_dict["TABLE_CA_TYPE"][index]
		except (IndexError, KeyError):
			return "Unknown"

	def getCAStatus(self):
		""" True or False """
		"""Syntax	 TruthValue 1 true 2 false"""
		return self.lookupstr("dr5000StatusDecodeCurrentProgramScrambled") in ["1", 1]

	def getBissStatus(self):

		"""biss1(2),
		bisse1(3),
		bisse2(4)
		"""

		"""JP 08/01/2013 IRD does not return the correct result on SNMP Poll
		d = {"1":"Off","2":"On","3":"On","4":"On"}
		if self.getCAStatus():
			return self.lookup_replace('Biss Status', d)
		else:
			return "Off"
		"""
		return ""

	def getFrameRate(self):
		try:
			numerator = int(self.lookupstr('frame rate num'))
		except ValueError:
			numerator = 0.0
		try:
			denominator = int(self.lookupstr('frame rate den'))
		except ValueError:
			denominator = 1.0
		try:
			qty = float(old_div(numerator, denominator))
		except ZeroDivisionError:
			qty = 0
		return ("%.2fHz" % qty).replace(".00", "")

	def getVResol(self):

		return self.lookupstr('video vertical resolution')

	def getinput_selection(self):
		""" Input type"""
		k = "dr5000StatusInputType"
		d = {"1": "IP", "2": "ASI", "3": "SAT", "4": "DS3"}
		return self.lookup_replace(k, d)

	def getlockState(self):
		""" return True on Bitrate when not using SAT"""
		if self.getinput_selection() == "SAT":
			d = {"1": "Lock", "2": "Unlock"}
			return self.lookup_replace('SatLockState', d)
		else:
			stat = ["Unlock", "Lock"]
			return stat[int(self.getinputTsBitrate()) > 0]

	def getinputTsBitrate(self):
		""" in kbps """

		key = 'inputtsbitrate'
		try:
			d = int(self.lookupstr(key)) * 1000  # kbps to bps
		except ValueError:
			d = 0
		return d

	def getinSatSetupModType(self):
		key = 'dr5000StatusInputSatModulation'
		d = {"1": "unknown", "2": "qpsk", "3": "8psk", "4": "16apsk", "5": "32apsk"}
		return self.lookup_replace(key, d)

	def getinSatSetupInputSelect(self)->int:
		""" DR5000 """
		key = 'dr5000ChannelConfigurationInputSatInterface'
		inp = self.lookupstr(key)
		try:
			return int(inp)
		except ValueError:
			return 1

	def getinSatSetupRollOff(self):

		d = {"4": "0.20", "2": "0.35", "3": "0.25", "1": "0"}
		return self.lookup_replace('dr5000StatusInputSatRollOff', d)

	def getVState(self):
		d = {"1": "Running", "2": "Stopped"}
		return self.lookup_replace('video state', d)

	def getAsiOutEncrypted(self):
		d = {"1": "Decrypted", "2": "Encrypted"}
		return self.lookup_replace('asi output mode', d)

	def getinSatSetupSatelliteFreq(self):
		""" Take kHz Return MHz """
		hz = 100000
		khz = 1000
		try:
			SatelliteFreqFloat = float(self.lookupstr('inSatSetupSatelliteFreq'))
		except ValueError:
			SatelliteFreqFloat = 0

		SatelliteFreqFloat = (old_div(SatelliteFreqFloat, khz))
		finalSatelliteFreq = str(SatelliteFreqFloat)
		##print finalsymrate
		# This code is to compensate for inconsistencies in the D2S frequency table where
		# sometimes we have .0 at the end sometimes we don't
		# services.py then uses LIKE ...% to get it to match
		if (finalSatelliteFreq[(len(finalSatelliteFreq) - 2):] == ".0"):
			finalSatelliteFreq = finalSatelliteFreq[:(len(finalSatelliteFreq) - 2)]
		return finalSatelliteFreq

	def getinSatSetupSymbolRate(self):
		""" Take KSPS return KSPS """
		key = "inSatSetupSymbolRate"
		try:
			symbolRateFloat = float(self.lookupstr(key))
		except ValueError:
			symbolRateFloat = 0
		symbolRateFloat = (symbolRateFloat)
		finalsymrate = str(symbolRateFloat)
		##print finalsymrate
		if (finalsymrate[(len(finalsymrate) - 2):] == ".0"):
			finalsymrate = finalsymrate[:(len(finalsymrate) - 2)]
		return finalsymrate

	def getIPoutEncrypted(self):
		""" IP output encrypted"""
		d = {"1": "Decrypted", "2": "Encrypted"}
		return self.lookup_replace('ip output scramble', d)

	def getinSatSetupFecRate(self):
		"""Return FEC rate. Normally Auto"""

		d = {"1": "unknown", "2": "1/4", "3": "1/3", "4": "2/5", "5": "1/2", "6": "3/5", "7": "2/3",
		     "8": "3/4", "9": "4/5", "10": "5/6", "11": "6/7", "12": "7/8", "13": "8/9", "14": "9/10"}
		return self.lookup_replace('SatStatusFEC', d)

	def getIPInputUsesVlan(self):
		return self.lookupstr("ip input has vlan") in ["1", 1]

	def getIPInputVlanID(self):
		return self.lookupstr("ip input vlan ID")

	def getIPInputAddress(self):
		ip = self.lookupstr("ip input multicast address")
		octets = []
		for octet in ip.split(" "):
			try:
				octets.append(int(octet, 16))
			except ValueError:
				continue
		if len(octets) != 4:
			return "0.0.0.0"
		return "%d.%d.%d.%d" % tuple(octets)

	def getIPInputUDPPort(self):
		return self.lookupstr("ip input udp port")

	def getNumServices(self):
		n = self.lookupstr("numServices")
		try:
			n = int(n)
		except:
			n = 0
		return n

	def refresh(self):
		""" Refresh method of Dr5000 """

		try:
			self.snmp_res_dict.update(snmp.get(self.getoids(), self.ip))


		except Exception as e:

			self.set_offline(f"Error with SNMP Get {e}")
		if len(list(self.snmp_res_dict.keys())) < len(list(self.getoids().keys())):
			self.oid_mask()

		if len(self.snmp_res_dict) == 0:
			self.set_offline("Empty SNMP Res Dict")
		else:
			self.set_online()
		if len(self.bulkoids()) != 0:
			if self.getNumServices():
				self.snmp_res_dict.update(snmp.getbulk(self.bulkoids(), self.ip, self.getNumServices() + 1))

		try:
			self.refreshCounter += 1
		except AttributeError:
			self.refreshCounter = 0
		refresh_params = []
		if not self.getRefreshType("lock"):  # Did we just lock? full refresh next time.
			if any([self.getlockState() == "Lock", int(self.getinputTsBitrate()) > 1]):
				refresh_params.append("full")

		try:
			refresh_params += [self.getinput_selection(),
			                   ["", "Locked"][self.getlockState() == "Lock"],
			                   ["", "Locked"][int(self.getinputTsBitrate()) > 1]
			                   ]
		except KeyError:
			refresh_params = ["full"]
		except ValueError:
			refresh_params = ["full"]
		self.set_refreshType(" ".join(refresh_params).lower())
		self.refreshCounter += 1

	def updatesql(self):
		sql = ["UPDATE status SET status = '%s'  " % self.getStatus()]
		sql += ["asi='%s'" % self.getinput_selection()]
		sql += ["muxbitrate='%s' " % self.getinputTsBitrate()]
		sql += ["muxstate='%s' " % self.getlockState()]
		# Full Only                                                                ]
		if self.getRefreshType("full"):
			sql += ["asioutencrypted='%s'" % self.getAsiOutEncrypted()]
			sql += ["ipoutencrypted='%s' " % self.getIPoutEncrypted()]
			sql += ["numServices='%s' " % self.getNumServices()]

		if self.getRefreshType("sat"):
			sql += ["frequency='%s'" % self.getinSatSetupSatelliteFreq()]
			sql += ["symbolrate='%s'" % self.getinSatSetupSymbolRate()]
			sql += ["fec='%s'" % self.getinSatSetupFecRate()]
			sql += ["rolloff='%s'" % self.getinSatSetupRollOff()]
			sql += ["modulationtype='%s'" % self.getinSatSetupModType()]
			sql += ["ebno='%s' " % self.getEbno()]
			sql += ["pol='%s' " % self.getPol()]
			sql += ["sat_input='%i' " % self.getinSatSetupInputSelect()]

		if self.getRefreshType("lock"):
			sql += ["servicename = '%s' " % self.getServiceName()]
			sql += ["aspectratio ='%s' " % self.getAspectRatio()]
			sql += ["castatus='%s' " % self.getCAType()]
			sql += ["videoresolution='%s' " % self.getVResol()]
			sql += ["framerate='%s' " % self.getFrameRate()]
			sql += ["videostate='%s'" % self.getVState()]
			sql += ["ServiceID='%s' " % self.getServiceID()]

		if self.getRefreshType("ip"):
			sql += ["ipinusesvlan='%d' " % self.getIPInputUsesVlan()]
			sql += ["ipinaddr='%s' " % self.getIPInputAddress()]

		sql += ["updated= CURRENT_TIMESTAMP "]

		sql = ", ".join(sql)
		sql += "WHERE id = %i; " % self.getId()
		return sql
