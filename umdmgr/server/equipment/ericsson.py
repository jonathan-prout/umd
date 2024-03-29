from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import subprocess
from builtins import hex
from builtins import range
from past.utils import old_div

from helpers.logging import log
from server.equipment.generic import IRD
from server import gv
from helpers import alarm, snmp

snmp.gv = gv  # in theory we don't want to import explictly the server's version of gv


class TT1260(IRD):

	def __init__(self, equipmentId, ip, name, *args, **kwargs):
		super(TT1260, self).__init__()
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "TT1260"
		super(TT1260, self).__init__()

	def getinSatSetupModType(self):
		key = 'inSatModType'
		d = {"5": "DVB-S2", "2": "DVB-S"}
		return self.lookup_replace(key, d)

	def updatesql(self):
		return "UPDATE status SET status = '%s' , servicename = '%s', aspectratio ='%s', ebno='%s', pol='%s', castatus='%s', videoresolution='%s', framerate='%s',videostate='%s',asioutencrypted='%s',frequency='%s',symbolrate='%s', updated= CURRENT_TIMESTAMP ,fec='%s',rolloff='%s',modulationtype='%s',muxbitrate='%s',muxstate='%s', asi='%s', sat_input='%i' WHERE id = %i; " % (
		self.getStatus(), self.getServiceName(), self.getAspectRatio(), self.getEbno(), self.getPol(),
		self.getBissStatus(), self.getVResol(), self.getFrameRate(), self.getVState(), self.getAsiOutEncrypted(),
		self.getinSatSetupSatelliteFreq(), self.getinSatSetupSymbolRate(), self.getinSatSetupFecRate(),
		self.getinSatSetupRollOff(), self.getinSatSetupModType(), self.getinputTsBitrate(), self.getlockState(),
		self.getinput_selection(), self.getinSatSetupInputSelect(), self.getId())

	def getinput_selection(self):
		""" Sat or ASI Different on each"""
		if self.getinSatSetupSatelliteFreq() == "0":
			return "ASI"
		else:
			return "SAT"


class RX1290(IRD):

	def __init__(self, equipmentId, ip, name, *args, **kwargs):

		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "RX1290"
		super(RX1290, self).__init__()

	def refresh(self):
		""" Refresh method of class """
		""" removed import snmp here """
		try:
			refresh_params = [self.getinput_selection(),
							["", "Locked"][self.getlockState() == "Lock"],
							["", "Locked"][int(self.getinputTsBitrate()) > 1]
							]
		except KeyError:
			refresh_params = ["full"]
		except ValueError:
			refresh_params = ["full"]
		self.set_refreshType(" ".join(refresh_params).lower())

		try:
			self.snmp_res_dict = snmp.get(self.getoids(), self.ip)
			self.set_online()
		except Exception as e:
			self.set_offline(f"Error with SNMP Get {e}")
		if len(list(self.snmp_res_dict.keys())) < len(list(self.getoids().keys())):
			self.oid_mask()

		if len(self.snmp_res_dict) == 0:
			self.set_offline("Empty SNMP Res Dict")
		if len(self.oid_getBulk) != 0:
			try:
				self.snmp_res_dict.update(snmp.walk(self.bulkoids(), self.ip))
			except subprocess.CalledProcessError:
				self.set_offline("Error with SNMP Get Bulk")
		try:
			self.refreshCounter += 1
		except AttributeError:
			self.refreshCounter = 0

		if not self.getRefreshType("lock"):  # Did we just lock? full refresh next time.
			if any([self.getlockState() == "Lock", int(self.getinputTsBitrate()) > 1]):
				self.set_refreshType("full")

	def updatesql(self):
		# return  "UPDATE status SET status = '%s' , servicename = '%s', aspectratio ='%s', ebno='%s', pol='%s', castatus='%s', videoresolution='%s', framerate='%s',videostate='%s',asioutencrypted='%s',frequency='%s',symbolrate='%s',fec='%s',rolloff='%s',modulationtype='%s',asi='%s',muxbitrate='%s', sat_input='%i' WHERE id = %i; " %(self.getStatus(),self.getServiceName(),self.getAspectRatio(),self.getEbno(),self.getPol(),self.getBissStatus(),self.getVResol(),self.getFrameRate(),self.getVState(),self.getAsiOutEncrypted(),self.getinSatSetupSatelliteFreq(),self.getinSatSetupSymbolRate(),self.getinSatSetupFecRate(),self.getinSatSetupRollOff(),self.getinSatSetupModType(),self.getinput_selection(),self.getinputTsBitrate(),self.getinSatSetupInputSelect(),self.getId())
		# ALL
		sql = ["UPDATE status SET status = '%s'  " % self.getStatus()]
		sql += ["asi='%s'" % self.getinput_selection()]
		sql += ["muxstate='%s' " % self.getlockState()]
		sql += ["muxbitrate='%s' " % self.getinputTsBitrate()]
		# Full Only
		if self.getRefreshType("full"):
			sql += ["asioutencrypted='%s'" % self.getAsiOutEncrypted()]
			sql += ["ServiceID='%s' " % self.getServiceID()]
			sql += ["numServices='%s' " % self.getNumServices()]

		# SAT IN                                                         ]
		if self.getRefreshType("sat"):
			sql += ["ebno='%s' " % self.getEbno()]
			sql += ["pol='%s' " % self.getPol()		]
			sql += ["frequency='%s '"% self.getinSatSetupSatelliteFreq()  ]
			sql += ["symbolrate='%s '"% self.getinSatSetupSymbolRate()    ]
			sql += ["fec='%s '"% self.getinSatSetupFecRate()              ]
			sql += ["rolloff='%s '"% self.getinSatSetupRollOff()          ]
			sql += ["modulationtype='%s '"% self.getinSatSetupModType()   ]
			sql += ["sat_input='%i '"% self.getinSatSetupInputSelect()    ]
		# Locked                                                          ]
		if self.getRefreshType("locked"):   
			sql +=[ "servicename = '%s'  "% self.getServiceName()         ]
			sql +=[ "aspectratio ='%s'  "% self.getAspectRatio()          ]
			sql +=[ "castatus='%s'  "% self.getCAStatus()                 ]
			sql +=[ "videoresolution='%s'  "% self.getVResol()            ]
			sql +=[ "framerate='%s'  "% self.getFrameRate()               ]
			sql +=[ "videostate='%s' "% self.getVState()                  ]

		sql += ["updated= CURRENT_TIMESTAMP "                            ]
		sql = ", ".join(sql)
		sql += " WHERE id = %i; " %self.getId()
		return sql

	def getinSatSetupModType(self):
		key = 'inSatModType'
		d = {"2": "DVB-S2", "1": "DVB-S"}
		return self.lookup_replace(key, d)

	def getNumServices(self):
		key = "Table_Service_ID"
		if key in self.snmp_res_dict:
			return len(self.snmp_res_dict[key])
		else:
			return 0

	def getDirectorStatus(self):
		try:
			return int(self.lookup("director_encrypted")) == 2
		except (ValueError, TypeError):
			return False

	def getCAStatus(self):
		try:
			castatus = int(self.lookup('castatus'))
		except (ValueError, TypeError):
			castatus = 0
		if self.getBissStatus() == "BISS":
			return "0x2600"
		elif self.getDirectorStatus():
			return "0x1010"

		elif castatus == 2:

			ca = self.lookup('CASID')
			if ca == "":
				ca = 0
			try:
				return hex(int(ca))
			except TypeError:
				return "CLEAR"
		else:
			return "CLEAR"

	def getinput_selection(self):
		d = {"1": "ASI", "2": "SAT"}
		return self.lookup_replace('input_selection ', d)


class RX8200(IRD):

	def __init__(self, equipmentId, ip, name, *args, **kwargs):

		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "RX8200"
		super(RX8200, self).__init__()

	def getlockState(self):
		d = {"1": "Lock", "0": "Unlock"}
		return self.lookup_replace('LockState', d)

	def getinputTsBitrate(self):
		key = 'inputtsbitrate '
		s = self.lookupstr(key) + "000"  # kbps to bps
		return s

	def refresh(self):
		""" Refresh method of Rx8200 """
		try:
			refresh_params = [self.getinput_selection(),
							  ["", "Locked"][self.getlockState() == "Lock"],
							  ["", "Locked"][int(self.getinputTsBitrate()) > 1]
							  ]
		except KeyError:
			refresh_params = ["full"]
		except ValueError:
			refresh_params = ["full"]
		self.set_refreshType(" ".join(refresh_params).lower())

		try:
			if not hasattr(self, "snmp_res_dict"):
				self.snmp_res_dict = {}
			self.snmp_res_dict.update(snmp.get(self.getoids(), self.ip))

		except Exception as e:
			self.set_offline(f"Error with SNMP Get {e}")
			return
		if len(list(self.snmp_res_dict.keys())) < len(list(self.getoids().keys())):
			self.oid_mask()

		if len(self.snmp_res_dict) == 0:
			self.set_offline("Empty SNMP Res Dict")
		else:
			self.set_online("Non Empty SNMP Res Dict")
		if len(self.bulkoids()) != 0:
			if self.getNumServices():
				self.snmp_res_dict.update(snmp.getbulk(self.bulkoids(), self.ip, self.getNumServices() + 1))

		try:
			self.refreshCounter += 1
		except AttributeError:
			self.refreshCounter = 0

		if not self.getRefreshType("lock"):  # Did we just lock? full refresh next time.
			if any([self.getlockState() == "Lock", int(self.getinputTsBitrate()) > 1]):
				self.set_refreshType("full")

	def updatesql(self):
		sql = ["UPDATE status SET status = '%s'  " % self.getStatus()]
		sql += ["updated= CURRENT_TIMESTAMP "]

		sql += ["asi='%s'" % self.getinput_selection()]
		sql += ["muxbitrate='%s' " % self.getinputTsBitrate()]
		sql += ["muxstate='%s' " % self.getlockState()]
		# Full Only   
		if self.getRefreshType("full"):
			sql += ["asioutencrypted='%s'" % self.getAsiOutEncrypted()]
			sql += ["numServices='%s' " % self.getNumServices()]

		if self.getRefreshType("sat"):
			sql += ["sat_input='%i'" % self.getinSatSetupInputSelect()]
			sql += ["frequency='%s'" % self.getinSatSetupSatelliteFreq()]
			sql += ["ebno='%s' " % self.getEbno()]
			sql += ["symbolrate='%s'" % self.getinSatSetupSymbolRate()]
			sql += ["fec='%s'" % self.getinSatSetupFecRate()]
			sql += ["rolloff='%s'" % self.getinSatSetupRollOff()]
			sql += ["modulationtype='%s'" % self.getinSatSetupModType()]
			sql += ["pol='%s' " % self.getPol()]
		if self.getRefreshType("lock"):
			sql += ["ServiceID='%s' " % self.getServiceID()]
			sql += ["servicename = '%s' " % self.getServiceName()]
			sql += ["aspectratio ='%s' " % self.getAspectRatio()]
			sql += ["castatus='%s' " % self.getCAStatus()]
			sql += ["videoresolution='%s' " % self.getVResol()]
			sql += ["framerate='%s' " % self.getFrameRate()]
			sql += ["videostate='%s'" % self.getVState()]
		sql = ", ".join(sql)
		sql += " WHERE id = %i; " % self.getId()
		return sql

	def getinSatSetupModType(self):
		key = 'inSatModType'
		d = {"1": "DVB-S2", "0": "DVB-S"}
		return self.lookup_replace(key, d)

	def getinSatSetupInputSelect(self) ->int:
		"""For RX8200
		# {channel_1(0),channel_2(1), channel_3(2), channel_4(3), channel_5(4), channel_6(5), channel_7(6), channel_8(7)}"""
		key = 'inSatSetupInputSelect '
		inp = self.lookupstr(key)
		try:
			return int(inp) + 1
		except ValueError:
			return 1

	def getinSatSetupRollOff(self):
		"""for RX8200 """
		d = {"0": "0.20", "1": "0.35", "2": "0.20"}
		return self.lookup_replace('inSatSetupRollOff ', d)

	def getinSatSetupFecRate(self):
		"""Return FEC rate. Normally Auto"""
		# {auto(0), fec_1_2(102), fec_1_3(103), fec_1_4(104),fec_2_3(203),fec_2_5(205),fec_3_4(304), fec_3_5(305),fec_4_5(405), fec_5_6(506), fec_6_7(607), fec_7_8(708),fec_8_9(809), fec_9_10(910),fec_unknown(999)
		d = {"999": "0", "102": "1/2", "103": "1/3", "104": "1/4", "203": "2/3", "205": "2/5", "304": "3/4",
			 "305": "3/5", "405": "4/5", "506": "5/6", "607": "6/7", "708": "7/8", "809": "8/9", "910": "9/10",
			 "0": "Auto"}
		return self.lookup_replace('inSatSetupFecRate', d)

	def getinput_selection(self):
		d = {"0": "ASI", "1": "SAT", "2": "SAT", 3: "IP"}
		return self.lookup_replace('input_selection ', d)

	def getServiceName(self):
		try:
			Table_Service_ID = list(self.snmp_res_dict["Table_Service_ID"])
			Table_Service_Name = list(self.snmp_res_dict["Table_Service_Name"])
			ServiceID = self.snmp_res_dict["ServiceID"]
		except KeyError:
			return ""
		for x in range(len(Table_Service_ID)):
			try:
				v = Table_Service_ID[x]
				v = v.replace('"', '')
				v = v.replace('\n', '')
				v = v.replace(' ', '')
				Table_Service_ID[x] = int(v)
			except ValueError:
				Table_Service_ID[x] = -1
		try:
			pos = Table_Service_ID.index(int(ServiceID))
			serviceName = Table_Service_Name[pos]
			return self.processServiceName(serviceName)
		except (ValueError, TypeError, KeyError):
			return ""

	def getCAStatus(self):

		try:
			Table_Service_ID = list(self.snmp_res_dict["Table_Service_ID"])
			tableEncryptionType = list(self.snmp_res_dict["tableEncryptionType"])
			ServiceID = self.snmp_res_dict["ServiceID"]
		except KeyError:
			return self.getBissStatus()
		for x in range(len(Table_Service_ID)):
			try:
				v = Table_Service_ID[x]
				v = v.replace('"', '')
				v = v.replace('\n', '')
				v = v.replace(' ', '')
				Table_Service_ID[x] = int(v)
			except ValueError:
				Table_Service_ID[x] = -1
		try:
			pos = Table_Service_ID.index(int(ServiceID))
			encType = tableEncryptionType[pos].strip()
			return encType
		except (ValueError, TypeError, KeyError):
			return self.getBissStatus()

	def getEbno(self):
		ebno = self.lookupstr('Eb / No')
		try:
			ebno = ebno.strip()
			ebno = ebno.replace(' ', '')
			ebno = ebno.replace('"', '')

			final = ebno.replace(" ", "")
			final = ebno.replace("+", "")
		except (ValueError, TypeError, AttributeError):
			final = ""
		if len(ebno) <= 1:
			final = ""
		return final

	def getAspectRatio(self):

		d = {"1": "16:9", "2": "4:3"}

		return self.lookup_replace('aspect ratio', d)

	def getPol(self):
		d = {"0": "Y", "1": "X"}
		return self.lookup_replace('polarisation', d)

	def getBissStatus(self):
		d = {"0": "Off", "1": "BISS"}
		return self.lookup_replace('Biss Status', d)

	def getFrameRate(self):
		# d = {"1":"Unknown","2":"25Hz","3":"30Hz","4":"50Hz","5":"60Hz","6":"29.97Hz","7":"59.97Hz"}
		fr = self.lookupstr('video frame rate')
		try:
			fr = float(fr)
		except (ValueError, TypeError):
			fr = 0
		fr = old_div(fr, 1000)
		st = "%sHz" % fr
		st = st.replace(".0", "")
		return st

	def determine_subtype(self):
		""" determine Sub Type. Returns string and
		should be processed outside the class as the idea is to replace with the correct device class"""
		""" removed import snmp here """

		# d = {'DeviceType':".1.3.6.1.4.1.1773.1.1.1.7.0"}
		d = {'inputCardType': ".1.3.6.1.4.1.1773.1.3.208.2.1.1.0"}  #
		# Integer32 {unknown(0); asi(1); sat_qpsk(2); ofdm(3); sat_16Qam(4); g057(5); sat_turbo_demod1(6); sat_hd(7);ip_input_g037(8); ipi_input(9); local_asi(10); atm_e3(11); atm_ds3(12); ip_input_g036(13);vsbCard_g062(14);
		subtypes = {
			19: "RX8200-4RF",
			21: "RX8200-2RF"
		}

		try:
			resdict = snmp.get(d, self.ip)
			self.offline = False
		except Exception: # NOQA: PyBroadException
			self.offline = True
			resdict = {'inputCardType': "OFFLINE"}
		if 'inputCardType' in resdict:

			try:
				return subtypes[int(resdict['inputCardType'])]
			except KeyError:
				return "Rx8200"
			except ValueError:
				if gv.loud:
					log(resdict, self, alarm.level.Major)
				self.offline = True
				return "OFFLINE"
		else:
			if gv.loud:
				log(resdict, self, alarm.level.Major)
			self.offline = True
			return "OFFLINE"




class RX8200_2RF(RX8200):
	def __init__(self, equipmentId, ip, name, *args, **kwargs):
		super(RX8200_2RF, self).__init__(equipmentId, ip, name)
		self.modelType = "RX8200-2RF"
		self.getoid()


class RX8200_4RF(RX8200):
	def __init__(self, equipmentId, ip, name, *args, **kwargs):
		super(RX8200_4RF, self).__init__(equipmentId, ip, name)
		self.modelType = "RX8200-4RF"
		self.getoid()
