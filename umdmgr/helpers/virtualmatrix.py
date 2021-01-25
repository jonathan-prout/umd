#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import
from .matrix.generic import matrix
from .infosource.sql import mysql
import threading
""" Matrix Interface """

""" Matrix abstraction class """



class virtualMatrix( mysql, matrix):
	def __init__(self, name):
		self.lock = threading.RLock() #Just to eliminate a race between$
		#super(virtualMatrix, self).__init__(name, "10.73.196.238", "umd", "umd", "matrix")
		super(virtualMatrix, self).__init__(name, "localhost", "umd", "umd", "matrix")
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
		self.openPrefs()
		self.getSizeAndLevels()
		self.refresh()
		
	def refresh(self):
		with self.lock:
			self.dbclose() #MYSQL BUG!!
			self.dbConnect()
			inout = ((self.input,"input"), (self.output,"output"))
			for d, table in inout:
				cmd = 'SELECT `name`,`port`,`level` FROM `%s` WHERE `matrixid` = %d'%(table, self.prefsDict["mtxId"])
				res = self.qselect(cmd)
				for row in res:
					try:
						name, port, level = row
						port = int(port) + self.countFrom1
						level = int(level)
					except ValueError:
						continue
					if level not in list(d.keys()):
						d[level] = {}
					d[level][port] = name
			cmd = "SELECT `status`.`input`, `status`.`output`, `status`.`levels` FROM `status` WHERE (`status`.`matrixid` ={});".format(self.prefsDict["mtxId"])
			res = self.qselect(cmd)
			for src, dest, levels in res:
				for c in levels:
					level= int(c)
					xpc = True
					try:
						if self.xpointStatus[level][dest + self.countFrom1] == src + self.countFrom1:
							xpc = False
					except:
						pass
					if xpc:
						self.onXPointChange( dest, src, level)
		
		
	def onXPointChange(self, dest, src, level):
		if level not in self.xpointStatus:
				self.xpointStatus[level] = {}
		self.xpointStatus[level][dest - self.countFrom1] = src - self.countFrom1
		try:
			print(self.name +" %s -> %s"%(self.input[level][src + self.countFrom1],self.output[level][dest + self.countFrom1] ))
		except KeyError:
			try:
				print(self.name +" %s -> %s"%(self.input[0][src + self.countFrom1],self.output[0][dest + self.countFrom1] ))
			except:
				print(self.name +" %s -> %s"%(dest + self.countFrom1 ,src + self.countFrom1))
			
	def sourceNameFromDestName(self, destName):
		with self.lock:
			srcNr = -1
			srcName = ""
			for level in list(self.output.keys()):
				for op, name in self.output[level].items():
					if name == destName:
						#self.xpointStatus[level][dest][src]
						if level in self.xpointStatus:
							if op in self.xpointStatus[level]:
								srcNr = self.xpointStatus[level][op]
						if  srcNr == -1 :
							for lvl, d in self.xpointStatus.items():
								if op in d:
									srcNr = d[op]
									break
						if srcNr > -1:
							if srcNr in self.input[level]:
								return self.input[level][srcNr]
							else:
								try:
									for lvl, d in self.output.items():
										if srcNr in d:
											return d[srcNr]
								except TypeError:
									print(f"Warning outputs not set on {self}")
		return srcName
		
		
	
