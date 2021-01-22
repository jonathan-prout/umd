import socket

from client.multiviewer import tsl



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
		try:
			self.sock.write(packet)
			self.set_online("OK")
		except (socket.error, TimeoutError) as e:
			self.set_offline(str(e))

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
						dmesg = self.writeline(videoInput, level, line, mode, colour= sm.colour)
						packet.append(dmesg)
						packet_commands += 1
						if packet_commands <= 9:
							try:
								self.sock.write(packet)
								self.set_online("OK")
							except (socket.error, TimeoutError) as e:
								self.set_offline(str(e))
							packet = tsl.TslPacket()
							packet_commands = 0
		if packet_commands > 0:
			try:
				self.sock.write(packet)
				self.set_online("OK")
			except (socket.error, TimeoutError) as e:
				self.set_offline(str(e))

		if self.fullref:
			self.qtruncate()

	def writeline(self, videoInput, level, line, mode, colour="#e3642d", buffered=True):

		try:
			addr = self.lookup(videoInput, level)
		except (KeyError, ValueError):
			print("videoIn, %s, level %s not found" % (videoInput, level))
			return

		dmesg = tsl.Dmesg(addr, f"{line};{colour}")
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
				"C/N": 200 + i,
				"REC": 200 + i
			}
			self.lookuptable[i] = d
