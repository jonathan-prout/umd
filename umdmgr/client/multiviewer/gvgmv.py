import socket

from client.multiviewer import tsl
from client.status import status_message
from helpers import alarm
from helpers.logging import log


class GvMv(tsl.TslMultiviewer):
	size = 48
	MAX_LABEL_LEN = 56

	def __init__(self, url: str, mvid: int, name: str):
		super(GvMv, self).__init__(url, mvid, name)
		self.make_default_input_table()
		self.write_status("UMD MANAGER CONNECTED", queued=False)
		self.clearalarms()

	def writeline(self, videoInput, level, line, mode= None, colour="#e3642d", buffered=True):

		try:
			addr = self.lookup(videoInput, level)
		except (KeyError, ValueError):
			print("videoIn, %s, level %s not found" % (videoInput, level))
			return
		if level in ["TOP", "BOTTOM"]:
			line = line[:self.MAX_LABEL_LEN]
			txt = f"{line};{colour}"
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

	def refresh(self):
		packet = tsl.TslPacket()
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
						dmesg = self.writeline(videoInput, level, line, mode, colour=sm.colour)
						if alarmText:
							log(dmesg, self, alarm.level.OK)
						packet.append(dmesg)
						packet_commands += 1
						if packet_commands <= 9:
							self.writepacket(packet)
							packet = tsl.TslPacket()
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
					packet = tsl.TslPacket()
					packet_commands = 0

		if packet_commands > 0:
			self.writepacket(packet)

		if self.fullref:
			self.qtruncate()


	def make_default_input_table(self):
		self.lookuptable = {}
		for i in range(1, self.size + 1):
			d = {
				"TOP": i,
				"BOTTOM": 100 + i,
				"C/N": 200 + i,
				"REC": 200 + i,
				"COMBINED": 200 + i
			}
			self.lookuptable[i] = d
