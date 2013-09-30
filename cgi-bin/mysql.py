#!/usr/bin/python
import os, re, sys,time,datetime
import threading, MySQLdb

class mysql:
	dhost="localhost"
	duser="umd"
	dpass="umd"
	dname="UMD"
	db = None
	cursor= None
	semaphore = None
	mutex = None

	def __init__(self):
		global dhost
		try:
			#print "Opening Database Connection...."
			mysql.db = MySQLdb.connect(mysql.dhost,mysql.duser,mysql.dpass,mysql.dname)

		except MySQLdb.Error, e:
			now = datetime.datetime.now()
			print "Database error at ", now.strftime("%H:%M:%S")
			print "Error %d: %s" % (e.args[0], e.args[1])
			mysql.db.close()
			sys.exit(1)
			
		
	def qselect(self,sql):
		""" semaphore & mutex lock to access share database """
		mysql.semaphore.acquire()
		mysql.mutex.acquire()
		
		mysql.cursor = mysql.db.cursor()
		mysql.cursor.execute("set autocommit = 1")
		#print "\n Mysql Class: I'm going to execute ", sql
		mysql.cursor.execute(sql)
		##mysql.cursor.commit()
		data = mysql.cursor.fetchall()
		
		""" semaphore & mutex lock to release locked share database """
		mysql.mutex.release()
		mysql.semaphore.release()		
		return data
	
	def close(self):
		#print "Closing database....."
		mysql.db.close()

