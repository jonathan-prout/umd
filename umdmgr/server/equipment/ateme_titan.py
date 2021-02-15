import typing

from helpers.interfaceproxy import DictKeyProxy
from helpers.logging import log
from server.equipment.generic import IRD, GenericIRD
from server import gv
from helpers import alarm, httpcaller
import time
import json

class HTTPError(Exception):
	pass


class Titan(IRD, DictKeyProxy):
	""" ATEME Titan Edge version 2.3.2 """

	def __init__(self, equipmentId, ip, name, subequipment=None):
		super(Titan, self).__init__()
		self.equipmentId = equipmentId
		self.ip = ip
		self.name = name
		self.modelType = "Titan"
		self.subequipment = subequipment
		self.data = {}
		self.seralisabledata = ["ip", "equipmentId", "name", "subequipment", "online", "modelType", "refreshType", "refreshCounter",
		                        "data"]


	def refresh(self):

		try:
			response, stringfromserver = httpcaller.get(self.ip, '80', f'decoder/api/channels/{self.subequipment}')
			if response['status'] != '200':
				raise HTTPError()
			self.online = True
		except (HTTPError, TimeoutError) as e:
			log(f"{e} error getting the url 'http://{self.ip}:80/decoder/api/channels/{self.subequipment}'", self,
				alarm.level.critical)
			self.online = False
			return

		jdata = json.loads(stringfromserver)
		self.set_get_decoder_api_channels_id_content(jdata)



	def set_get_decoder_api_channels_id_content(self, content):
		self.setKey("updated", "OK")
		self.setKey("id", content.get("id"))
		self.set_is_running(content.get("is_running"))
		self.set_is_enabled(content.get("is_enabled"))
		self.set_configuration(content.get("configuration"))
		self.set_status(content.get("status"))

	def set_status(self, content):

		self.set_status_decode(content.get("decode"))
		self.set_status_source(content.get("source"))

	def set_status_input(self, content):
		input_id = 0
		for _input in content:
			input_ports = []
			input_id += 1
			ifacename = f"input_{input_id}"
			iface = self.getInterface(ifacename)


			iface.setKey("ts_bitrate", _input.get("bitrate", 0) )
			iface.setKey("ts_lock", _input.get("tsLocked", False))

			ip = _input.get("ip", {})
			connector = f"{ifacename}_ip"

			ipport = self.getInterface(connector)
			input_ports.append(connector)


			ipport.setKey("rtp", ip.get("isRtp"))
			ipport.setKey("packet_counter", ip.get("packetCounter", 0))
			ipport.setKey("missing_packet_counter", ip.get("missingPacketCounter", 0))
			ipport.setKey("input_error_rate", ip.get("inputErrorRate", 0))
			ipport.setKey("output_error_rate", ip.get("outputErrorRate", 0))
			ipport.setKey("jitter", ip.get("jitter", 0))

			sat = _input.get("sat", {})
			satname = f"{ifacename}_sat"
			satport = self.getInterface(satname)
			input_ports.append(satname)


			satport.setKey("lock", sat.get("isLocked"))
			satport.setKey("carrier_noise_ratio", sat.get("cnr"))
			satport.setKey("margin", sat.get("cnrMargin"))
			satport.setKey("bit_error_rate", sat.get("ber"))
			satport.setKey("fec", sat.get("fec"))
			satport.setKey("roll_off", sat.get("rollOff"))
			satport.setKey("pilot_symbols", sat.get("pilots"))

	def set_status_decode(self, content):
		decoder = self.getInterface("decoder")
		currentProgram = content.get("currentProgram", {})
		decoder.setKey("service_id", currentProgram.get("id", None))
		video = currentProgram.get("video" , {})
		decoder.setKey("video_status", video.get("hasActivity", False))
		decoded = video.get("decoded", {})
		decoder.setKey("video_codec", decoded.get("codec"))
		decoder.setKey("video_bitrate", decoded.get("bitrate", 0) / 1000000 )
		decoder.setKey("width",  decoded.get("width", 0))
		decoder.setKey("height", decoded.get("height", 0))
		try:
			frame_rate = decoded.get("fpsNum", 0) / decoded.get("fpsDen", 0)
		except ZeroDivisionError:
			frame_rate = 0
		decoder.setKey("frame_rate", frame_rate)
		decoder.setKey("aspect_ratio", decoded.get("dar"))

	def set_status_source(self, content):
		self.set_status_input(content.get("input"))
		decoder = self.getInterface("decoder")
		tsDescriptor = content.get("tsDescriptor", {})
		services = {}
		for program in tsDescriptor.get("program"):
			service_id = program.get("programNumber", 0)
			PCR = program.get("pcrPid")
			name = program.get("serviceName")
			service = {
				"service_id": service_id,
				"PCR": PCR,
				"name": name,
				"PIDs": program.get("stream")

			}

			services[service_id] = service
		decoder.setKey("services", services)
		decoder.setKey("service_count", tsDescriptor.get("programCount", 0))

		input_id = 0
		inputs = content.get("input", [])

	def set_configuration(self, content):
		decoder = self.getInterface("decoder")
		decoder.setKey("name", content.get("name"))
		input_id = 0
		inputs = content.get("source", {}).get("input", [])
		input_coll = []
		enabled = []
		for _input in inputs:
			input_ports = []
			input_id += 1
			ifacename = f"input_{input_id}"
			iface = self.getInterface(ifacename)
			input_coll.append(ifacename)

			iface.setKey("enabled", _input.get("isEnabled", False))
			if _input.get("isEnabled", False):
				enabled.append(f"input_{input_id}")
			availableInputs = []
			inputMapping = {}

			asi = _input.get("asi", {})
			connector = asi.get("connector", {}).get("name", "")
			asiname = f"{ifacename}_asi"


			input_ports.append(asiname)
			asiport = self.getInterface(asiname)

			availableInputs.append(asiname)
			inputMapping["asi"] = asiport
			asiport.setKey("connector", asi.get("connector", {}).get("name", ""))

			ip = _input.get("ip", {})
			connector = f"{ifacename}_ip"

			ipport = self.getInterface(connector)
			input_ports.append(connector)

			availableInputs.append(connector)
			inputMapping["ip"] = ipport
			ipport.setKey("address", ip.get("address"))
			ipport.setKey("port", ip.get("port"))
			ipport.setKey("connector", ip.get("interface", ""))

			sat = _input.get("sat", {})

			satname = f"{ifacename}_sat"
			satport = self.getInterface(satname)
			input_ports.append(satname)

			availableInputs.append(satname)
			inputMapping["sat"] = satport
			satport.setKey("mode", sat.get("mode"))
			satport.setKey("symbol_rate", sat.get("symbolRate", 0) )
			satport.setKey("downlink_frequency", sat.get("downlinkFrequency", 0) / 1000)
			satport.setKey("lo_frequency", sat.get("oscillatorFrequency", 0) / 1000)

			satport.setKey("polarization", sat.get("lnb", {}).get("polarization"))
			satport.setKey("high_band", sat.get("lnb", {}).get("send22kTone", False))
			satport.setKey("connector", sat.get("connector", {}).get("name", ""))
			iface.setKey("input", _input.get("type"))

		if len(enabled) == 1:
			decoder.setKey("input", enabled[0])
		else:
			decoder.setKey("input", None)

	def set_is_running(self, value):
		decoder = self.getInterface("decoder")
		decoder.setKey("running", value)

	def set_is_enabled(self, value):
		decoder = self.getInterface("decoder")
		decoder.setKey("enabled", value)

	def getCAType(self):
		decoder = self.getInterface("decoder")
		current_service_id = decoder.getKey("service_id", 0)
		services = decoder.getKey("services", {})
		current_service = services.get(current_service_id, {})
		pcr = current_service.get("PCR", 0)
		for pid in current_service.get("PIDs", []):
			if pid.get("pid", 0) == pcr:
				return pid.get("caType", "")
		return ""

	def updatesql(self):
		decoder = self.getInterface("decoder")
		selected_input_name = decoder.getKey("input", "UNKNOWN")
		selected_input = self.getInterface(selected_input_name)
		asi = self.getInterface(selected_input_name + "_asi")
		ip  = self.getInterface(selected_input_name + "_ip")
		sat = self.getInterface(selected_input_name + "_sat")

		sql = ["UPDATE status SET status = '%s'  " % self.getStatus()]
		sql += ["asi='%s'" % selected_input.getKey("input", "").upper()]
		sql += ["muxbitrate='%s' " % selected_input.getKey("ts_bitrate", "0")]
		sql += ["muxstate='%s' " % ["Unlock", "Lock"][selected_input.getKey("ts_locked", False)]]

		# TODO: Maybe? I don't know if the Titan can do this. Ignore for now
		# sql += ["asioutencrypted='%s'" % "True"]
		# sql += ["ipoutencrypted='%s' " % "True"]
		sql += ["numServices='%s' " % decoder.getKey("service_count", 0)]
		sql += ["frequency='%s'" % sat.getKey("downlink_frequency", "")]
		sql += ["symbolrate='%s'" % sat.getKey("symbol_rate", "")]
		sql += ["fec='%s'" % sat.getKey("fec", "")]
		sql += ["rolloff='%s'" % sat.getKey("roll_off", "")]
		sql += ["modulationtype='%s'" % sat.getKey("mode", "")]
		sql += ["ebno='%s' " % sat.getKey("margin", "")]
		sql += ["pol='%s' " % sat.getKey("polarization", "").upper()[0]]

		# TODO: Ask Ateme why this is broken. Sat connector name shows as emptystring.
		# For now this will be cabled on the basis of one sat input per decoder
		# So it dowsn't matter and the best idea is to always return 1
		sql += ["sat_input='%i' " % 1]

		current_service_id = decoder.getKey("service_id", 0)
		services = decoder.getKey("services", {})
		current_service = services.get(current_service_id, {})

		sql += ["servicename = '%s' " % current_service.get("name", "")]
		sql += ["aspectratio ='%s' " % decoder.getKey("aspect_ration", "")]
		sql += ["castatus='%s' " % self.getCAType()]
		sql += ["videoresolution='%s' " % decoder.getKey("height", 0)]
		sql += ["framerate='%s' " % decoder.getKey("frame_rate", 0)]
		sql += ["videostate='%s'" % ["Stopped", "Running"][decoder.getKey("video_status", False)]]
		sql += ["ServiceID='%s' " % current_service_id]
		sql += ["ipinaddr='%s' " % ip.getKey("address", "0.0.0.0")]

		sql += ["updated= CURRENT_TIMESTAMP "]

		sql = ", ".join(sql)
		sql += "WHERE id = %i; " % self.getId()
		return sql




