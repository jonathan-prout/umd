""" UMD Manager 11
	Kaleido multiviewers
	git note: moved from mukltiviewer.py
"""
import queue
from helpers import telnethelper

from client.multiviewer.generic import TelnetMultiviewer
from client.status import status_message
from client import gv
import xml.etree.ElementTree as etree


class kaleido(TelnetMultiviewer):
	mv_type = "Kaleido"
	port = 13000
	size = 96
	timeout = 10

	def __init__(self, host, mvid, name):
		super(kaleido, self).__init__(mvid, name)
		self.AlarmCapable = True
		self.lowAddressBug = False
		self.mv_type = "Kaleido"
		self.port = 13000
		self.size = 96
		self.q = queue.Queue(10000)
		self.host = host

		self.fullref = False
		self.make_default_input_table()
		self.tel = None
	def start(self):
		self.connect()

	def connect(self):

		"""
		# Set the signal handler and a 5-second alarm
		signal.signal(signal.SIGALRM, self.errorHandler)
		signal.alarm(5)
		"""
		self.shout("%s: Connecting to to %s" % (self.name, self.host))
		try:

			assert (gv.programTerminationFlag == False)
			self.tel = telnethelper.Telnet(self.host, self.port)
			self.tel.write("Hello\n")
			self.tel.read_until("<nack/>", self.timeout)
			self.set_online()
			self.write_status("UMD manager connected", queued=False)
			self.shout("Connected to %s" % self.host)
		except:
			self.set_offline("init")
			self.shout("%s: Cannot connect to %s" % (self.name, self.host))
		finally:
			# signal.alarm(0)          # Disable the alarm
			pass

	def make_default_input_table(self):
		self.lookuptable = {}
		for i in range(1, self.size + 1):
			d = {
				"TOP": "0" + str(i),
				"BOTTOM": 100 + i,
				"C/N": 500 + i,
				"REC": 600 + i
			}
			self.lookuptable[i] = d

	def lookup(self, videoInput, level):
		return self.lookuptable[int(videoInput)][level]

	def writeline(self, videoInput, level, line, mode, *args, **kwargs):

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
		"""   
			# Set the signal handler and a 5-second alarm
			signal.signal(signal.SIGALRM, self.errorHandler)
			signal.alarm(5)
			"""
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

	def setAction(self, actionName):

		cmd = '<setKFireAction>set name="%s"</setKFireAction>\n' % actionName
		a = ""
		try:
			self.tel.write(cmd)
			a = self.tel.read_until("<ack/>", self.timeout)
			if "<ack/>" not in a:
				self.shout(a)
		except:
			if "<nack/>" in a:
				self.shout("Multiviewer did not recognise the action named %s" % actionName)
			else:
				self.set_offline("writeline, %s, %s " % (actionName, a))
		finally:
			# signal.alarm(0)          # Disable the alarm
			pass

	def getActionList(self):
		a = ""
		cmd = '<getKActionList/>\n'
		try:
			self.tel.write(cmd)
			a = self.tel.read_until("</kActionList>", self.timeout)
			if "</kActionList>" not in a:
				self.shout(a)
				return []
		except:
			if "<nack/>" in a:
				return []
		xmlData = etree.fromstring(a)
		returnList = []
		for el in xmlData.findall("action"):
			returnList.append(el.text)
		return returnList

	def refresh(self):
		while not self.q.empty():
			if self.fullref:
				break
			sm = self.q.get()
			if isinstance(sm, status_message):
				# print self.host + ": status %s//%s"%(sm.topLabel, sm.bottomLabel)
				# for alarm in [sm.cnAlarm, sm.recAlarm]:
				sm.cnAlarm = {True: "MAJOR", False: "DISABLE"}[sm.cnAlarm]
				sm.recAlarm = {True: "MAJOR", False: "DISABLE"}[sm.recAlarm]

				for videoInput, level, line, mode in sm:
					if not line: line = " "
					if not self.get_offline():
						if not self.matchesPrevious(videoInput, level, line):
							self.writeline(videoInput, level, line, mode)
			elif isinstance(sm, (list, tuple)):
				try:
					videoInput = sm[0]
					level = sm[1]
					line = sm[2]
				except IndexError:
					continue

				self.writeline(videoInput, level, line, mode=status_message.textMode)
		if self.fullref:
			self.qtruncate()

	def __del__(self):
		try:
			self.tel.close()
		except:
			pass

	def clearalarms(self):
		""" KX has alarms on on startup, so clear them """
		if self.get_offline():
			return
		self.write_status("Clearing Alarms", queued=False)
		alarm_addresses = {"REC": 500, "C/N": 600}
		for alarm_type in ["REC", "C/N"]:

			for mv_input in range(self.size):
				addr = alarm_addresses[alarm_type] + mv_input + 1
				cmd = '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>\n' % (addr, "DISABLE")
				a = ""
				try:
					self.tel.write(cmd)
					a = self.tel.read_until("<ack/>", self.timeout)
					if "<ack/>" not in a:
						self.shout(a)
				except Exception as e:
					if "<nack/>" in a:
						self.shout("NACK ERROR in writeline when writing %s" % cmd)
					else:
						self.set_offline("ClearAlarms, %s, %s " % (addr, e))
						return

class KX(kaleido):
	mv_type = "KX"
	port = 13000
	size = 96
	AlarmCapable = True
	lowAddressBug = False
	fullref = False
	clearAlarmsOnConnect = True

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.q = queue.Queue(1000)

		self.make_default_input_table()


	def connect(self):
		super(KX, self).connect()
		if self.clearAlarmsOnConnect:
			self.clearalarms()


class K2(kaleido):
	mv_type = "K2"
	AlarmCapable = False
	lowAddressBug = False
	port = 13000
	size = 32
	fullref = False

	def __init__(self, *args, **kwargs):
		super(K2, self).__init__(*args, **kwargs)
		# self.False = True #Note to self pick out variable names I can remember
		# what what
		self.q = queue.Queue(100)
		self.host = host

		self.fullref = False
		self.make_default_input_table()



class KX16(KX):
	mv_type = "KX-16"
	size = 16


class KXQUAD(KX):
	mv_type = "KX-QUAD"
	size = 4
