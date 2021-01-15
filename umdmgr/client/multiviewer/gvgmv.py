from umdmgr.client import gv, labelmodel
from umdmgr.client.multiviewer import tsl
from umdmgr.client.multiviewer.generic import get_mv_input_from_database
from umdmgr.client.umdclient import inputStrategies


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
		while not self.q.empty():
			if self.fullref:
				break
			sm = self.q.get()
			if sm:
				sm.cnAlarm = {True: "MAJOR", False: "DISABLE"}[sm.cnAlarm]
				sm.recAlarm = {True: "MAJOR", False: "DISABLE"}[sm.recAlarm]

				for videoInput, level, line, mode in sm:
					if not line: line = " "
					if not self.get_offline():
						if not self.matchesPrevious(videoInput, level, line):
							self.writeline(videoInput, level, line, mode)
		if self.fullref:
			self.qtruncate()

	def getStatusMesage(self, mvInput, mvHost=self.host):
		with gv.equipDBLock:

			happy_statuses = ["RUNNING"]
			poll_status = getPollStatus().upper()
			display_status = gv.display_server_status.upper()

			sm = tsl.TslPacket
			# Get the multiviewer input strategy from the database for this input
			res = get_mv_input_from_database(mvHost, mvInput)

			if all((poll_status in happy_statuses, display_status in happy_statuses)):
				try:
					if gv.equip[int(res["equipment"])] is not None:
						tlOK = True
					else:
						tlOK = False
					e = None
				except KeyError as e:
					tlOK = False

				if all((int(res["strategy"]) == int(inputStrategies.equip), tlOK)):
					sm = gv.equip[res["equipment"]].getStatusMessage()
					assert sm is not None
					sm.strategy = "equip"
				elif res["strategy"] == inputStrategies.matrix:
					mtxIn = gv.mtxLookup(res["inputmtxname"])
					if gv.getEquipByName(mtxIn):
						sm = gv.equip[gv.getEquipByName(mtxIn)].getStatusMessage()
						sm.strategy = "matrix + equip"
						assert sm is not None
					else:
						sm = labelmodel.matrixResult(mtxIn).getStatusMessage()
						assert sm is not None
						sm.strategy = "matrix no equip"
				elif res["strategy"] == inputStrategies.indirect:
					sm = labelmodel.matrixResult(res["inputmtxname"]).getStatusMessage()
					assert sm is not None
					sm.strategy = "indirect"
				elif res["strategy"] == inputStrategies.label:
					if res["customlabel1"]:
						sm.topLabel = res["customlabel1"]
					if res["customlabel2"]:
						sm.bottomLabel = res["customlabel2"]
					sm.strategy = "label"
			else:
				try:
					if gv.equip[int(res["equipment"])] is not None:
						tlOK = True
					else:
						tlOK = False
					e = None
				except KeyError as e:
					tlOK = False
				if all((int(res["strategy"]) == int(inputStrategies.equip), tlOK)):
					sm.topLabel = gv.equip[int(res["equipment"])].isCalled()
					sm.bottomLabel = " "
					sm.strategy = "equip"
				elif res["strategy"] == inputStrategies.label:
					if res["customlabel1"]:
						sm.topLabel = res["customlabel1"]
					if res["customlabel2"]:
						sm.bottomLabel = res["customlabel2"]
					sm.strategy = "label"
				else:
					sm.topLabel = res["inputmtxname"]
					# sm.bottomLabel = "%s, %s %s,%s"%(res["equipment"],len(gv.equip.keys()),e, int(res["strategy"]) )
					sm.bottomLabel = " "
					sm.strategy = "matrix"
				if mvInput % 16 == 1:
					sm.bottomLabel = "Display: %s, Polling:%s" % (display_status, poll_status)

			sm.mv_input = mvInput

		return sm

	def writeline(self, videoInput, level, line, mode):

		try:
			addr = self.lookup(videoInput, level)
		except (KeyError, ValueError):
			print("videoIn, %s, level %s not found" % (videoInput, level))
			return
		a = ""
		if mode == status_message.alarmMode:
			if self.AlarmCapable:
				cmd = '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>\n' % (addr, line)
			else:
				return
		else:
			if self.lowAddressBug:
				if addr < 100:
					addr = "0" + str(addr)
			cmd = '<setKDynamicText>set address="%s" text="%s" </setKDynamicText>\n' % (addr, line)
		try:
			self.tel.write(cmd)
			# print cmd
			a = self.tel.read_until("<ack/>", self.timeout)
			if "<ack/>" not in a:
				if "<nack/>" in a:
					self.shout("%s: NACK ERROR in writeline when writing %s" % (self.host, cmd))
				else:
					self.shout(a)
		except:

			self.set_offline("writeline, %s, %s " % (line, a))
		finally:
			# signal.alarm(0)          # Disable the alarm
			pass