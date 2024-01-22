import socket
import struct

from client.multiviewer import generic
from helpers import alarm
from helpers.logging import log

DLE = b"\xFE"
STX = b"\x02"


class TslPacket(object):
	def __init__(self):
		self.version = 0
		self.flags = 0
		self.screen = 0
		self.DMSG = []

	def append(self, dmesg):
		self.DMSG.append(dmesg)

	def __bytes__(self):
		b = struct.pack("<b", self.version)
		b += struct.pack("<b", self.flags)
		b += struct.pack("<H", self.screen)
		for dmesg in self.DMSG:
			b += bytes(dmesg)
		b = struct.pack("<H", len(b)) + b
		return b


class Tally(object):
	OFF = 0
	RED = 1
	GREEN = 2
	AMBER = 3


class Dmesg(object):
	def __init__(self, index, text, left_tally=Tally.OFF, text_tally=Tally.OFF, right_tally=Tally.OFF):
		self.index = index
		self.text = text
		self.text_tally = text_tally
		self.left_tally = left_tally
		self.right_tally = right_tally

	def __bytes__(self) -> bytes:
		b = struct.pack("<H", self.index)
		ctrl = 0
		ctrl += (self.left_tally << 4)
		ctrl += (self.text_tally << 2)
		ctrl += (self.right_tally << 0)
		b += struct.pack("<H", ctrl)
		txt = self.text.encode("ASCII")
		b += struct.pack("<H", len(txt))
		b += txt
		return b

	def __repr__(self):
		tallyName = ["OFF", "RED", "GREEN", "AMBER"]
		lt = tallyName[self.left_tally]
		rt = tallyName[self.right_tally]
		tt = tallyName[self.text_tally]
		return f"<Dmesg index {self.index} left_tally {lt} right_tally {rt} text_tally {tt} text '{self.text}'>"


class TcpSocket(object):
	def __init__(self, host, port):
		self.sock = None
		self.host = host
		self.port = port

	def connect(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.settimeout(5)
		self.sock.connect((self.host, self.port))


	def write(self, packet):
		return self.sock.send(DLE + STX + bytes(packet))

	def read(self, length: int):
		return self.sock.recv(length)


class UdpSocket(object):
	def __init__(self, host, port):
		self.sock = None
		self.host = host
		self.port = port

	def connect(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def write(self, packet):
		return self.sock.sendto(DLE + STX + bytes(packet), (self.host, self.port))


class TslMultiviewer(generic.multiviewer):
	"""
	TSL Multiviewer class
	url in the format of udp://host:port or tcp://host:port
	"""

	def __init__(self, url: str, mvid:int, name:str):
		self.url = url
		self.sock = None
		self.lookuptable = {}
		super(TslMultiviewer, self).__init__(mvid, name)

		self.make_default_input_table()

	def start(self):
		self.connect()

	def _split_url(self):
		try:
			protocol, host, port = self.url.split(":")
		except (IndexError, ValueError):
			self.set_offline("url should be in the format of udp://host:port or tcp://host:port")
			return
		host = host.replace("//", "")
		port = int(port)
		return protocol, host, port

	@property
	def host(self):
		protocol, host, port = self._split_url()
		return host

	@property
	def port(self):
		protocol, host, port = self._split_url()
		return port

	@property
	def protocol(self):
		protocol, host, port = self._split_url()
		return protocol

	def connect(self):
		"""
		url in the format of udp://host:port or tcp://host:port
		"""

		protocol, host, port = self._split_url()
		self.set_status("Connecting")
		if protocol.lower() == "tcp":
			self.sock = TcpSocket(host, port)
			self.set_status("Connecting TCP")
			self.sock.connect()
			self.set_online("Connected")
		elif protocol.lower() == "udp":
			self.sock = UdpSocket(host, port)
			self.set_status("Connecting UDP")
			self.sock.connect()
			self.set_online("Connected")
		else:
			self.set_offline("url should be in the format of udp://host:port or tcp://host:port")
			return

	def clearalarms(self):
		""" KX has alarms on on startup, so clear them """
		if self.get_offline():
			return
		self.qtruncate()
		for videoInput in self.lookuptable.keys():
			sm = status_message()
			sm.topLabel = ""
			sm.bottomLabel = ""
			sm.mv_input = videoInput
			self.put(sm)
		sm = status_message()
		sm.topLabel = ""
		sm.bottomLabel = "UMD Manager Connected"
		sm.mv_input = 1
		self.put(sm)
		self.refresh()

	def refresh(self):
		packet = TslPacket()
		packet_commands = 0
		while not self.q.empty():
			if self.fullref:
				break
			sm = self.q.get()
			if isinstance(sm, status_message):
				if sm.cnAlarm:
					sm.cnAlarm = "Low C/N Margin"
				else:
					sm.cnAlarm = ""
				if sm.recAlarm:
					sm.recAlarm = "Rec Off"
				else:
					sm.recAlarm = ""

				alarmText = ", ".join([s for s in [sm.cnAlarm, sm.recAlarm] if s != ""])

				mode = sm.textMode
				videoInput = sm.mv_input

				for level, line in [
					["TOP", sm.topLabel],
					["BOTTOM", sm.bottomLabel],
					["COMBINED", alarmText]]:
					if not line:  # Checks against None. Might not be necessary.
						line = ""
					if not self.get_offline() and not self.matchesPrevious(videoInput, level, line):
						dmesg = self.writeline(videoInput, level, line, mode)
						if alarmText:
							log(dmesg, self, alarm.level.OK)
						packet.append(dmesg)
						packet_commands += 1
						if packet_commands <= 9:
							self.writepacket(packet)
							packet = TslPacket()
							packet_commands = 0

			elif isinstance(sm, (list, tuple)):
				try:
					videoInput = sm[0]
					level = sm[1]
					line = sm[2]
				except IndexError:
					continue

				dmesg = self.writeline(videoInput, level, line)
				packet.append(dmesg)
				packet_commands += 1
				if packet_commands <= 9:
					self.writepacket(packet)
					packet = TslPacket()
					packet_commands = 0

		if packet_commands > 0:
			self.writepacket(packet)

		if self.fullref:
			self.qtruncate()

	def writepacket(self, packet) -> int:
		""" Write to socket return how many bytes writen"""
		n = 0
		try:
			n = self.sock.write(packet)
			self.set_online("OK")
		except (socket.error, TimeoutError) as e:
			self.set_offline(str(e))

		return n


	def writeline(self, videoInput, level, line, mode= None, buffered=True):

		try:
			addr = self.lookup(videoInput, level)
		except (KeyError, ValueError):
			print("videoIn, %s, level %s not found" % (videoInput, level))
			return
		if level in ["TOP", "BOTTOM"]:
			line = line[:self.MAX_LABEL_LEN]
			txt = line
		else:
			txt = line
		dmesg = tsl.Dmesg(addr, txt)
		if not buffered:
			packet = tsl.TslPacket()
			packet.append(dmesg)
			try:
				self.sock.write(packet)
				self.set_online("OK")
			except (socket.error, TimeoutError) as e:
				self.set_offline(str(e))
		return dmesg
	def make_default_input_table(self):
		self.lookuptable = {}
		for i in range(1, self.size + 1):
			d = {
				"TOP": i,
				"BOTTOM": 100 + i,
				"C/N": 500 + i,
				"REC": 600 + i,
				"COMBINED": 200 + i
			}
			self.lookuptable[i] = d

	def lookup(self, videoInput, level):
		return self.lookuptable[int(videoInput)][level]
