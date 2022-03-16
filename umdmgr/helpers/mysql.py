#!/usr/bin/python
from __future__ import print_function

import datetime
import threading
import time

import MySQLdb


import MySQLdb._exceptions # noqa

from helpers import alarm
from helpers.logging import log, logerr


class mysql(object):
	autocommit = False

	def __init__(self, dhost="localhost", duser="umd", dpass="umd", dname="UMD"):
		self.dhost=dhost
		self.duser=duser
		self.dpass=dpass
		self.dname=dname
		self.db = None
		self.cursor= None

		self.semaphore = threading.BoundedSemaphore(value=1)
		self.mutex = threading.RLock()

		self.reconnectsLeft = 11
		self.connected = False
		self.connect()
		
	def __repr__(self):
		status = ["Disconnected", "Connected"][self.connected]
		return f"<mysql connection {status} {self.duser}@{self.dhost}>"
		
	def connect(self):
		self.reconnectsLeft -=1
		if self.reconnectsLeft <10:
			log("Waiting before reconnecting to database. Retries left %d"% self.reconnectsLeft, self, alarm.level.Info)
			time.sleep(1)
		if self.reconnectsLeft < 0:
			if hasattr(self, "gv"):
				if hasattr(self.gv, "programCrashed"): # Applicable to server version
					self.gv.sql.programCrashed = True
					# noinspection PyUnresolvedReferences
					gv.programCrashed = True
			errorText = "Run out of database reconnects. Program should now close"		
			print("%s %s"%(time.strftime("%d-%m-%Y %H:%M:%S"), errorText))
			raise RuntimeError(errorText)
		try:

			log("Opening Database Connection....", self, alarm.level.OK)
			self.db = MySQLdb.Connection(self.dhost,self.duser,self.dpass,self.dname)
			self.cursor = self.db.cursor()
			self.connected = True

		except Exception as e:
			now = datetime.datetime.now()

			log("Database error on connection", self, alarm.level.Critical)
			logerr(str(self), alarm.level.Critical)
			try:
				self.close()
			except:
				pass
			#sys.exit(1)
			raise e

		

	def qselect(self,sql, require_lock = True, commit = None):
		""" semaphore & mutex lock to access share database takes sql command as string. Returns list"""
		if require_lock:
			if commit is None:
				commit = self.autocommit

			if self.semaphore:
				self.semaphore.acquire()
			if self.mutex:
				self.mutex.acquire()
		rows = []
		e = None
		
		""" If we get an error. We need to make sure that db lock is released before raising the error. """
		
		
		try:
			while not self.connected: # Hold on reconnect loop
				self.close()
				self.connect()
			
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
						rows += data.fetch_row(maxrows=0)
					except Exception:
						pass
					if commit:
						self.db.commit()

		except Exception as e:
			log("Database error on query", self, alarm.level.Critical)
			logerr(str(self), alarm.level.Critical)
			log(sql, self, alarm.level.critical)
			self.close()

		finally:
			""" semaphore & mutex lock to release locked share database """
			if require_lock:
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
		log("Closing database.....", self, alarm.level.Info)
		try:
			self.db.close()
		except (AttributeError, MySQLdb._exceptions.OperationalError):  # Hey bossy IDE it's not my fault they organize their packages like that
			pass
		finally:
			self.db = None
			self.connected = False
		
	def __del__(self):
		self.close()

