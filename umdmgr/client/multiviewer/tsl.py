import socket
import struct

from umdmgr.client.multiviewer import generic

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
		ctrl += (self.leftTally << 4)
		ctrl += (self.textTally << 2)
		ctrl += (self.rightTally << 0)
		b += struct.pack("<H", ctrl)
		txt = self.text.encode("ASCII")
		b += struct.pack("<H", len(txt))
		b += txt
		return b


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


class TslMultiviewer(generic.muiltiviewer):
	"""
	TSL Multiviewer class
	url in the format of udp://host:port or tcp://host:port
	"""

	def __init__(self, url: str):
		self.url = url
		self.sock = None
		self.lookuptable = {}
		super(TslMultiviewer, self).__init__()

	def connect(self):
		"""
		url in the format of udp://host:port or tcp://host:port
		"""
		try:
			protocol, host, port = self.url.split(":")
		except (IndexError, ValueError):
			self.set_offline("url should be in the format of udp://host:port or tcp://host:port")
			return
		host = host.replace("//", "")
		port = int(port)
		if protocol.lower() == "tcp":
			self.sock = TcpSocket(host, port)
			self.sock.connect()
		elif protocol.lower() == "udp":
			self.sock = UdpSocket(host, port)
			self.sock.connect()
		else:
			self.set_offline("url should be in the format of udp://host:port or tcp://host:port")
			return

	def make_default_input_table(self):
		self.lookuptable = {}
		for i in range(1, self.size + 1):
			d = {
				"TOP": i,
				"BOTTOM": 100 + i,
				"C/N": 500 + i,
				"REC": 600 + i
			}
			self.lookuptable[i] = d

	def lookup(self, videoInput, level):
		return self.lookuptable[int(videoInput)][level]
