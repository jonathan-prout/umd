#!/usr/bin/python
import os, re, sys,time,datetime
import threading, MySQLdb

class mysql:
	def __init__(self):
		self.dhost="localhost"
		self.duser="umd"
		self.dpass="umd"
		self.dname="UMD"
		self.db = None
		self.cursor= None
		self.semaphore = None
		self.mutex = None
		self.DBBAD = "oppps"
		try:
			#print "Opening Database Connection...."
			self.db = MySQLdb.Connection(self.dhost,self.duser,self.dpass,self.dname)
			self.cursor = self.db.cursor()

		except MySQLdb.Error, e:
			now = datetime.datetime.now()
			print "Database error at ", now.strftime("%H:%M:%S")
			print "Error %d: %s" % (e.args[0], e.args[1])
			self.db.close()
			#sys.exit(1)
			raise e
		
	def qselect(self,sql):
		""" semaphore & mutex lock to access share database takes sql command as string. Returns list"""
		self.semaphore.acquire()
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
					#self.db.commit()
					
					try:
						rows +=  data.fetch_row(maxrows=0)
					except:
						pass
		except Exception as e:
			pass
		
		
		
		
		finally:
			""" semaphore & mutex lock to release locked share database """
			self.mutex.release()
			self.semaphore.release()
		
		
		if e != None:
			raise(e)
		
		return rows
		
	def close(self):
		#print "Closing database....."
		self.db.close()

