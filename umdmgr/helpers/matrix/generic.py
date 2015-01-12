import time
import socket
from threading import Lock
class pointerVariable(object):
	""" class to make a variable act like a pointer """
	obj = None
	def __str__(self ):
		return str(self.obj)
	
	def __repr__(self):
		return '"%s"'%self.__str__()
	def set(self, assignment ):
		self.obj = assignment
	def __int__(self, ):
		return int(obj)
	def __float__(self ):
		return float(obj)
	def __unicode__(self, ):
		return self.__str__()
	

class matrix(object):
	""" Defines generic matrix interfaces """
	status = "No Status Set"
	debug = True
	mtxType = "Unset"
	countFrom1 = False
	hasManyLevels = True
	timeout = 0 # Set to a number to enable keepalive messages to be sent.
	subscription_timeout = 0 # set to a number to resubscribe if no xpoint data sent in a certain time (seconds)
	last_status_message = 0
	
	#def __init__(self, configpath):
	""" Configuration will be held in a conf file or url. It is up to the class to interpret this. """
	def shout(self, stuff):
		print "%s" % stuff
	def setStatus(self,s):
		if self.debug:
			print s
		self._status = s
	def getStatus(self):
		return self._status
		
	def get_offline(self):
			try:
					return self.offline
			except:
					return True

	def set_online(self):
		self.offline = False
		
	
	def set_offline(self, message = None):
		self.offline = True
		if message:
			self.setStatus(message)

	def srcNumberFromButtonNumber(self, number):
		""" returns the actual source number behind a button """
		return number + self.countFrom1
	def destNumberFromButtonNumber(self, number):
		""" returns the actual dest number behind a button""" 
		return number	+ self.countFrom1
						

	def errorHandler(self, error):
		print 'Error handler called with the following error: %s'% error.__repr__()
		
	def size(self,level):
		""" Return a tuple of two integers, destinations, sources for given level"""
		#return (0,0)
		raise NotImplementedError("This class has not implimented this!")
	def levels(self):
		""" return list of available level numbers """
		#return [0]
		raise NotImplementedError("This class has not implimented this!")
	def levelNames(self):
		""" return dict of available level numbers and their names"""
		#return {0:""}
		raise NotImplementedError("This class has not implimented this!")
	def destNames(self, level):
		""" return dict of available destination numbers and their names"""
		#return {0:""}
		raise NotImplementedError("This class has not implimented this!")
	def sourceNames(self, level):
		""" return dict of available destination numbers and their names"""
		#return {0:""} 
		raise NotImplementedError("This class has not implimented this!")
	def mtxStatus(self, level, lazy = False):
		""" return dict of available destination numbers and what is routed to them
		Lazy controls whether to do a full refresh or just get whatever the current status
		is plus any buffered messages
		"""
		#return {0:-1}
		raise NotImplementedError("This class has not implimented this!")
	def lock(self, level, destination, panel="None"):
		""" lock destination panel is string. True on Success"""
		return False
	
	def unLock(self, level, destination, panel):
		""" un lock destination. True on Success """
		return True
	
	def isLocked(self, level, destination):
		""" Is destination locked """
		return False
	def lockedBy(level, destination):
		""" who locked destination"""
		return "None"
	def take(self, level, destination, source):
		raise NotImplementedError("This class has not implimented this!")
	def qGet(self):
		""" Used for implimenting command queueing
		Usage:
		No error: Queue item processed
		Queue Empty: Queue now empty can move on now
		NotImplimentedError: Class does not support queueing, don't use command queueing interface
		Other Error to be handled by calling function or passed to errorHandler
		"""
		raise NotImplementedError("This class has not implimented this!")
	def refresh(self):
		""" Use for async xpoint processing
		"""
		pass
	
	def onXPointChange(self, source, dest, levels ):
		""" To be called when a crosspoint changes. Override when you need to do something when that happens
		source, dest int
		levels list
		"""
		pass
	

	def close(self):
		pass
	
	def qtruncate(self):
		raise NotImplementedError("This class has not implimented this!")
		
	def __del__(self):
		
		self.close()
		
class telnetMatrix(matrix):
	
	telnetLock = Lock()
	def connect(self):
		raise NotImplementedError("This subclass must have this implimented")
	
	def proc_status_message(self, sm): pass
	def proc_buffer(self, l): pass
	
	def subscribe(self):
		pass
	def unsubscribe(self):
		pass
	
	def keepAlive(self):
		if self.get_offline():
			self.connect()
		if self.timeout:
			if self.last_cmd_sent + self.timeout < time.time():
				try:
					wstr = self.keepAliveStr + self.retseq
					res = self.write_before_read(wstr, self.keepAliveResponse, 1)
					assert(self.keepAliveResponse in res)
					self.proc_buffer(res)
					self.last_cmd_sent = time.time()
				except EOFError, AssertionError:
					self.set_offline("keepalive")
			
	def read_buffer(self, buf=""):
		#buf = ""
		while 1:
			with self.telnetLock:
				txt = ""
				try:
					txt = self.tel.read_eager()
				except EOFError: 
					self.set_offline()
					return []
				if txt == "": break
				else:
					buf +=txt
		return buf.split(self.retseq)
	
	def read_blocking(self, buf=""):
		#buf = ""
		while 1:
			with self.telnetLock:
				txt = ""
				try:
					txt = self.tel.read_blocking(0.1)
				except EOFError: 
					self.set_offline()
					return []
				try:
					if txt == "": break
					if len(txt) < 1: break
				except ValueError, TypeError:
					break
				else:
					buf +=txt
		return buf.split(self.retseq)
	
	
	def write(self, s):
		with self.telnetLock:
			if self.debug: print ("->:%s"%s)
			try:
				self.tel.write(s)
			except EOFError, socket.error:
				self.set_offline("write")
			
	def read_until(self, s, timeout):
		with self.telnetLock:
			
			try:
				
				res =  self.tel.read_until(s, timeout)
				if self.debug: print ("<-:%s"%res)
				return res
			except EOFError, socket.error:
				self.set_offline("read_until")
	def write_before_read(self, writeString, readString, timeout):
		with self.telnetLock:
			if self.debug: print ("->:%s"%writeString)
			try:
				self.tel.write(writeString)
			except EOFError, socket.error:
				self.set_offline("write")
			try:
				
				res =  self.tel.read_until(readString, timeout)
				if self.debug: print ("<-:%s"%res)
				return res
			except EOFError, socket.error:
				self.set_offline("read_until")
	def close(self):
		try:
			self.tel.close()
		except AttributeError:
			pass
	def refresh(self):
		if not self.get_offline:
			self.proc_buffer(self.read_buffer())
