from umdmgr.client import gv, labelmodel
from umdmgr.client.multiviewer import tsl
from umdmgr.client.multiviewer.generic import get_mv_input_from_database, status_message
from umdmgr.client.umdclient import inputStrategies, getPollStatus


class GvMv(tsl.TslMultiviewer):
	def clearalarms(self):
		""" KX has alarms on on startup, so clear them """
		if self.get_offline():
			return
		self.writeStatus("Clearing Alarms", queued=False)
		alarm_address = 200
		packet = tsl.TslPacket()

		for mv_input in range(self.size):
			txt = tsl.Dmesg(203, "")
			txt.leftTally = tsl.Tally.OFF
			txt.rightTally = tsl.Tally.OFF
		self.sock.write(packet)

	def refresh(self):
		packet = tsl.TslPacket()
		packet_commands = 0
		while not self.q.empty():
			if self.fullref:
				break
			sm = self.q.get()
			if sm:
				sm.cnAlarm = {True: "Low C/N Margin", False: ""}[sm.cnAlarm]
				sm.recAlarm = {True: "NO REC", False: ""}[sm.recAlarm]

				for videoInput, level, line, mode in sm:
					if not line:
						line = " "
					if not self.get_offline() and not self.matchesPrevious(videoInput, level, line):
						dmesg = self.writeline(videoInput, level, line, mode)
						packet.append(dmesg)
						packet_commands += 1
						if packet_commands <= 9:
							self.sock.write(packet)
							packet = tsl.TslPacket()
							packet_commands = 0
		if packet_commands > 0:
			self.sock.write(packet)

		if self.fullref:
				self.qtruncate()

	def writeline(self, videoInput, level, line, mode, buffered=True):

		try:
			addr = self.lookup(videoInput, level)
		except (KeyError, ValueError):
			print("videoIn, %s, level %s not found" % (videoInput, level))
			return

		dmesg = tsl.Dmesg(addr, line)
		if not buffered:
			packet = tsl.TslPacket()
			packet.append(dmesg)
			self.sock.write(packet)
		return dmesg

	def make_default_input_table(self):
		self.lookuptable = {}
		for i in range(1, self.size + 1):
			d = {
				"TOP": "0" + str(i),
				"BOTTOM": 100 + i,
				"C/N": 200 + i,
				"REC": 200 + i
			}
			self.lookuptable[i] = d
