#!/usr/bin/env python
from matrix.generic import matrix
from infosource.sql import mysql
import threading
""" Matrix Interface """

""" Matrix abstraction class """



class virtualMatrix( mysql, matrix):
	def __init__(self, name):
		self.lock = threading.RLock() #Just to eliminate a race between$
		super(virtualMatrix, self).__init__(name, "10.73.196.238", "umd", "umd", "matrix")
		""" Start by passing name as string. Mysql handler as class instance """
		"""
		#self.lock = threading.RLock() #Just to eliminate a race between$
		self.name = name
		self.sql = mysql.mysql(dname="matrix")
		"""
		"""
		res = self.sql.qselect("SELECT `matrixes`.`id`FROM `matrixes` WHERE ( `matrixes`.`mtxName` LIKE '%s')"%self.name)
		try:
			self.mtxID = res[0][0]
		except IndexError:
			self.mtxID = 0
		"""
		self.xpointStatus = {}
		self.prefsDict = {}
		self.dbConnect()
		self.refresh()
		
	def refresh(self):
		with self.lock:
			self.openPrefs()
			self.getSizeAndLevels()
		
		
	def onXPointChange(self):
		pass
	
	def sourceNameFromDestName(self, destName):
		with self.lock:
			srcNr = None
			srcName = ""
			for level in self.output.keys():
				for op,name in self.output[level].iteritems():
					if name == destName:
						#self.xpointStatus[level][dest][src]
						if self.xpointStatus.has_key(level):
							if self.xpointStatus[level].has_key(op):
								srcNr = self.xpointStatus[level][op]
						if not srcNr:
							for lvl, d in self.xpointStatus.iteritems():
								if d.has_key(op):
									srcNr = d[op]
									break
						if srcNr:
							if self.input[level].has_key(srcNr):
								return self.input[level][srcNr]
							else:
								for lvl, d in self.output:
									if d.has_key(srcNr):
										return  d[srcNr]
		return srcName
		
		
	
