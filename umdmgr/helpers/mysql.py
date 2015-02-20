#!/usr/bin/python
import os, re, sys,time,datetime
import threading, MySQLdb

class mysql:
	autocommit = False
	def __init__(self, dhost="localhost", duser="umd", dpass="umd", dname="UMD"):
		self.dhost=dhost
		self.duser=duser
		self.dpass=dpass
		self.dname=dname
		self.db = None
		self.cursor= None
		#self.semaphore = None
		self.semaphore = threading.BoundedSemaphore(value=1)
		self.mutex = threading.RLock()
		#self.mutex = None
		self.DBBAD = "oppps"
		try:
			#print "Opening Database Connection...."
			self.db = MySQLdb.Connection(self.dhost,self.duser,self.dpass,self.dname)
			self.cursor = self.db.cursor()

		except Exception, e:
			now = datetime.datetime.now()
			print "Database error at ", now.strftime("%H:%M:%S")
			print "Error %s" % (e.__repr__())
			try:
				self.close()
			except:
				pass
			#sys.exit(1)
			raise e

		

	def qselect(self,sql):
		""" semaphore & mutex lock to access share database takes sql command as string. Returns list"""
		if self.semaphore:
			self.semaphore.acquire()
		if self.mutex:
			self.mutex.acquire()
		rows = []
		e = None
		
		""" If we get an error. We need to make sure that db lock is released before raising the error. """
		try:
			#self.cursor.execute("set autocommit = 1")
			#print "\n Mysql Class: I'm going to execute ", sql
			#self.cursor.execute(sql)
			for command in sql.split(";"): #SQL commands separated by ; but this can do one at a time
				if command not in ["", " "]: #there will always be one 0 len at the end
					#print "'" + command + "'"
					self.db.query(command + ";")
					data = self.db.use_result()
				
					
					
					#data = self.cursor.fetchall()
					
					
					try:
						rows +=  data.fetch_row(maxrows=0)
					except:
						pass
					if self.autocommit:
                                                self.db.commit()

		except Exception as e:
			with open("sqlerror.log", "a") as fobj:
				fobj.write( "%s,%s,%s"%(time.strftime("%d-%m-%Y %H:%M:%S"), e.__repr__(),sql) )
				print "%s SQL error %s, %s"%(time.strftime("%d-%m-%Y %H:%M:%S"), e.__repr__(),sql)
		
		
		
		finally:
			""" semaphore & mutex lock to release locked share database """
			if self.mutex:
				self.mutex.release()
			if self.semaphore:
				self.semaphore.release()
		
		"""
		if e != None:
			raise(e)
		"""
		return rows
		
	def close(self):
		#print "Closing database....."
		try:
			self.db.close()
		except AttributeError: pass
		
	def __del__(self):
		self.close()

