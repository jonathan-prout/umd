#!/usr/bin/python
import os, re, sys
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
	DBBAD = "oppps"

	def __init__(self):
		try:
			#print "Opening Database Connection...."

			mysql.db = MySQLdb.connect(mysql.dhost,mysql.duser,mysql.dpass,mysql.dname)
	

		except:
			print "Database Connection Error"
			#raise mysql.DBBAD
		
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

