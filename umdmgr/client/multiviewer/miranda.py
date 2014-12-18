""" UMD Manager 11
	Kaleido multiviewers
	git note: moved from mukltiviewer.py
	"""
	
import telnetlib, Queue, signal, time
from generic import telnet_multiviewer, status_message


		
class kaleido(telnet_multiviewer):
	mv_type = "Kaleido"
	port = 13000
	size = 96
	timeout = 10
	def __init__(self, host):
		self.mv_type = "Kaleido"
		self.port = 13000
		self.size = 96
		self.q = Queue.Queue(10000)
		self.host = host
		self.connect()
		self.fullref = False
		self.make_default_input_table()

	def connect(self):    
		
		"""
		# Set the signal handler and a 5-second alarm
		signal.signal(signal.SIGALRM, self.errorHandler)
		signal.alarm(5)
		"""
		try:
			from client import gv
			assert(gv.programTerminationFlag == False)
			self.tel = telnetlib.Telnet(self.host, self.port)
			self.tel.write("\n")
			self.tel.read_until(">", self.timeout)
			self.set_online()
			self.writeStatus("UMD manager connected", queued=False)
		except:
			self.set_offline("init")
			self.shout("Cannot connect to %s" %self.host)
		finally:
			#signal.alarm(0)          # Disable the alarm
			pass
	def make_default_input_table(self):
		self.lookuptable = {}
		for i in range(1, self.size+1):
			d = {
				"TOP": "0" + str(i),
				"BOTTOM": 100 + i,
				"C/N": 500 + i,
				"REC": 600 + i
			}
			self.lookuptable[i] = d
			
	def lookup(self, videoInput, level):
		 return self.lookuptable[int(videoInput)][level]
	
	def writeline(self, videoInput, level, line, mode):
		
			try:
				addr = self.lookup(videoInput, level)
			except:
				print "videoIn, %s, level %s not found"%(videoInput, level)
				return
			a = ""
			if mode == status_message.alarmMode:
				if self.AlarmCapable:
					cmd = '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>\n' %(addr, line)
				else:
					return
			else:
				if self.lowAddressBug:
					if addr < 100:
						addr = "0"+str(addr)
				cmd = '<setKDynamicText>set address="%s" text="%s" </setKDynamicText>\n' %(addr, line)
			"""   
			# Set the signal handler and a 5-second alarm
			signal.signal(signal.SIGALRM, self.errorHandler)
			signal.alarm(5)
			"""
			try:
				self.tel.write(cmd)
				a = self.tel.read_until("<ack/>", self.timeout)
				if "<ack/>" not in a:
					self.shout(a)
			except:
				if "<nack/>" in a:
					self.shout("NACK ERROR in writeline when writing %s"% cmd)
				else:
					self.set_offline("writeline, %s, %s "%(line,a) )
			finally:
				#signal.alarm(0)          # Disable the alarm
				pass
	def setAction(self, actionName):
		
		cmd = '<setKFireAction>set name="%s"</setKFireAction>\n'%actionName
		try:
			self.tel.write(cmd)
			a = self.tel.read_until("<ack/>", self.timeout)
			if "<ack/>" not in a:
				self.shout(a)
		except:
			if "<nack/>" in a:
				self.shout("Multiviewer did not recognise the action named %s"% actionName)
			else:
				self.set_offline("writeline, %s, %s "%(line,a) )
		finally:
			#signal.alarm(0)          # Disable the alarm
			pass

	def getActionList(self):
		import xml.etree.ElementTree as E
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
		xmlData = E.fromstring(a)
		returnList = []
		for el in xmlData.findall("action"):
			returnList.append(el.text)
		return returnList
	
	def refresh(self):
		while not self.q.empty():
			if self.fullref:
				break
			sm = self.q.get()
			if sm:
				print self.host + ": status %s//%s"%(sm.topLabel, sm.bottomLabel)
				for alarm in [sm.cnAlarm, sm.recAlarm]:
					alarm = {True:"MAJOR", False:"DISABLE"}[alarm]
					
				for videoInput, level, line, mode in sm:
					if not line: line = ""
					if not self.get_offline():
						if not self.matchesPrevious(videoInput, level, line):
							self.writeline(videoInput, level, line, mode)
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
		self.writeStatus("Clearing Alarms", queued=False)
		alarm_addresses = {"REC":500, "C/N":600}
		for alarm_type in ["REC", "C/N"]:
			
			for mv_input in range(self.size):
				addr = alarm_addresses[alarm_type] + mv_input +1
				cmd = '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>\n' %(addr, "DISABLE")
				a = ""
				try:
					self.tel.write(cmd)
					a = self.tel.read_until("<ack/>", self.timeout)
					if "<ack/>" not in a:
						self.shout(a)
				except Exception as e:
					if "<nack/>" in a:
						self.shout("NACK ERROR in writeline when writing %s"% cmd)
					else:
						self.set_offline("ClearAlarms, %s, %s "%(addr, e) )
						return
class KX(kaleido):
	mv_type = "KX"
	port = 13000
	size = 96
	AlarmCapable = True
	lowAddressBug = False
	fullref = False
	clearAlarmsOnConnect = True
	def __init__(self, host):
		
		self.q = Queue.Queue(1000)
		self.host = host

		self.make_default_input_table()
		self.connect()

	
	def connect(self):
		super(KX,self).connect()
		if self.clearAlarmsOnConnect:
			self.clearalarms()
		
class K2(kaleido):
	mv_type = "K2"
	AlarmCapable = False
	lowAddressBug = False
	port = 13000
	size = 32
	fullref = False
	
	def __init__(self, host):
		self.False = True #Note to self pick out variable names I can remember
		self.q = Queue.Queue(100)
		self.host = host
		
		self.fullref = False
		self.make_default_input_table()
		self.connect()

class KX16(KX):
	mv_type = "KX-16"
	size = 16

class KXQUAD(KX):
	mv_type = "KX-QUAD"
	size = 4
		
