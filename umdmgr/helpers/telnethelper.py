import telnetlib
import time
import select

from builtins import bytes, str
from time import monotonic as _time
from telnetlib import _TelnetSelector
import selectors


class Telnet(telnetlib.Telnet):
	def read_blocking(self, timeout=None):
		"""Read until some data is encountered or until timeout.

		whatever is available,
		possibly the empty string.  Raise EOFError if the connection
		is closed and no cooked data is available.

		"""

		self.process_rawq()

		if self.cookedq != b"":
			buf = self.cookedq
			self.cookedq = b""
			return buf.decode()
		if timeout is not None:
			deadline = _time() + timeout
		with _TelnetSelector() as selector:
			selector.register(self, selectors.EVENT_READ)
			while not self.eof:
				if selector.select(timeout):
					i = max(0, len(self.cookedq))
					self.fill_rawq()
					self.process_rawq()

					if i >= 0:
						buf = self.cookedq
						self.cookedq = b""
						return buf.decode()
				if timeout is not None:
					timeout = deadline - _time()
					if timeout < 0:
						break

		return self.read_very_lazy().decode()

	def read_until(self, match, timeout=None):
		"""Make bytes object of buffer for python3"""
		if isinstance(match, str):
			match = bytes(match.encode("ASCII"))
		return super(Telnet, self).read_until(match, timeout).decode()

	def write(self, buffer):
		"""Make bytes object of buffer for python3"""
		if isinstance(buffer, str):
			buffer = bytes(buffer.encode("ASCII"))
		return super(Telnet, self).write(buffer)


""" Telnet factory from bagels. Uncomment if required
telnetInstances = {}


def TelnetFactory(host, port):
	tel = telnetInstances.get((host, port), None)
	if tel is None:
		telnetInstances[(host, port)] = Telnet(host, port, timeout=5)  # Create new.
		log("New Telnet instance for {}:{} created".format(host, port), "Telnethelper", bagels.alarm.level.Debug)
	elif getattr(tel, "sock", 0) in [0, None]:  # Disconnected
		telnetInstances[(host, port)] = Telnet(host, port, timeout=10)
		log("Telnet instance for {}:{} disconnected. Making new one".format(host, port), "Telnethelper",
			bagels.alarm.level.Debug)
	else:
		log("Telnet instance for {}:{} already exists. Returning".format(host, port), "Telnethelper",
			bagels.alarm.level.Debug)
	return telnetInstances[(host, port)]
"""