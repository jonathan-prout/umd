""" Matrixes using MYSQL data
"""
from __future__ import print_function
from __future__ import absolute_import

from builtins import zip
from . import generic
import threading
import MySQLdb
import MySQLdb._exceptions
from .. import alarm
from ..logging import log


class mysql(generic.IInfoSourceMixIn):
	def __init__(self, name, host, duser, dpass, dbase, sqlLock=None):
		self.dhost = host
		self.duser = duser
		self.dpass = dpass
		self.dname = dbase
		self.name = name
		self.db = None
		self.cursor = None
		self.semaphore = None
		self.mutex = None
		self.DBBAD = "oppps"
		if not sqlLock:
			sqlLock = threading.RLock()
		self.sqlLock = sqlLock

		self.input = {}
		self.output = {}

	def dbMTime(self, table):
		cmd = "show table status from %s like '%s';" % (self.dname, table)
		try:
			return self.qselect(cmd)[0][11]
		except (MySQLdb.error, IndexError, TypeError):
			return None

	def dbConnect(self):
		""" Connect to dbase
		"""
		try:
			# print "Opening Database Connection...."
			self.db = MySQLdb.Connection(self.dhost, self.duser, self.dpass, self.dname)
			self.cursor = self.db.cursor()
			self.set_online()
		except Exception as e:

			# raise mysql.DBBAD
			""" Must be mixed in with an object that supports set_offline methods
			"""
			self.set_offline("Database Connection Error %s" % e.__repr__())

	# self.db.query("DO 0;")
	# self.db.commit()
	def openPrefs(self):
		cmd = 'SELECT `id`,`mtxName`,`type`,`address`,`capability` FROM `matrixes` WHERE `mtxName` = "%s"' % self.name
		res = self.qselect(cmd)
		if not len(res) == 1:
			self.set_offline("Database Error: There are multiple matrixes named %s" % self.name)
			return
		res = res[0]
		self.prefsDict["mtxId"] = int(res[0])
		self.prefsDict["mtxName"] = res[1]
		self.prefsDict["mtxProtocol"] = res[2]
		if len(res[3].split(":")) == 2:
			self.prefsDict["host"], self.prefsDict["port"] = res[3].split(":")
		else:
			self.prefsDict["host"] = res[3]
		self.prefsDict["capabilitiy"] = res[4].split(" ")

		self.input = {}
		self.output = {}
		inout = ((self.input, "input"), (self.output, "output"))
		for d, table in inout:
			cmd = 'SELECT `name`,`port`,`level` FROM `%s` WHERE `matrixid` = %d' % (table, self.prefsDict["mtxId"])
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

	def getSizeAndLevels(self):
		cmd = "SELECT `status`.`input`, `status`.`output`, `status`.`levels` FROM `status` WHERE (`status`.`matrixid` ={});".format(
			self.prefsDict["mtxId"])
		res = self.qselect(cmd)
		for src, dest, levels in res:
			for c in levels:
				level = int(c)
				# self.onXPointChange( dest, src, level)
				xpc = True
				try:
					if self.xpointStatus[level][dest + self.countFrom1] == src + self.countFrom1:
						xpc = False
				except (IndexError, KeyError, TypeError):
					pass
				if xpc:
					self.onXPointChange(dest, src, level)
				"""
				if not self.xpointStatus.has_key(level):
						self.xpointStatus[level] = {}
				self.xpointStatus[level][dest - self.countFrom1] = src - self.countFrom1
				"""

	def qselect(self, sql):
		""" semaphore & mutex lock to access share database takes sql command as string. Returns list"""
		# self.semaphore.acquire()
		# self.mutex.acquire()
		rows = []
		e = None

		""" If we get an error. We need to make sure that db lock is released before raising the error. """
		try:
			# self.cursor.execute("set autocommit = 1")
			# print "\n Mysql Class: I'm going to execute ", sql
			# self.cursor.execute(sql)
			for command in sql.split(";"):  # SQL commands separated by ; but this can do one at a time
				if command not in ["", " "]:  # there will always be one 0 len at the end
					# print "'" + command + "'"
					with self.sqlLock:
						self.db.query(command + ";")
						data = self.db.use_result()

					# data = self.cursor.fetchall()
					# self.db.commit()

					try:
						rows += data.fetch_row(maxrows=0)
					except MySQLdb.error:
						pass
		except Exception as e:
			pass




		finally:
			""" semaphore & mutex lock to release locked share database """
		# self.mutex.release()
		# self.semaphore.release()

		if e != None:
			raise (e)

		return rows

	def __del__(self):
		self.close()

	def close(self):

		try:
			log("Closing database.....", self, alarm.level.Info)
			self.db.close()
		except (AttributeError,
				MySQLdb._exceptions.OperationalError):  # Hey bossy IDE it's not my fault they organize their packages like that
			pass
		finally:
			self.db = None

	def levelNames(self):
		""" return dict of available item numbers and their names
		"""
		return dict(list(zip(list(self.input.keys()), list(self.input.keys()))))

	def destNames(self, level):
		""" return dict of available destination numbers and their names
		"""
		try:
			return self.output[int(level)].copy()
		except KeyError:
			return {}

	def sourceNames(self, level):
		""" return dict of available source numbers and their names
		"""
		try:
			return self.input[int(level)].copy()
		except KeyError:
			return {}

	def sources(self, level):
		""" return a List of the sources for a given level
		"""
		try:
			return list(self.input[int(level)].keys())
		except KeyError:
			return {}

	def destinations(self, level):
		""" return a List of the destination for a given level
		"""
		try:
			return list(self.input[int(level)].keys())
		except KeyError:
			return {}

	def size(self, level):
		""" Return a tuple of two integers, destinations, sources for given level
		"""
		try:
			return (len(list(self.output[int(level)].keys())), len(list(self.input[int(level)].keys())))
		except KeyError:
			return (0, 0)

	def levels(self):
		""" return list of available level numbers
		"""
		return list(self.input.keys())

	def onXPointChange(self, source, dest, levels):
		import time
		for level in levels:
			try:
				log("%s->%s" % (self.sourceNames(level)[source], self.destNames(level)[dest]), self, alarm.level.OK)
			except KeyError:
				log("%s->%s" % (source, dest), self, alarm.level.OK)

		with self.sqlLock:
			for lvl in levels:
				cmd = "SELECT `PRIMARY`  FROM `status` WHERE `matrixid` = {} AND `output` = {} AND `levels` LIKE '{}';".format(
					self.prefsDict["mtxId"], dest, lvl)

				try:
					primary = self.qselect(cmd)[0][0]
				except IndexError:
					primary = None
				except Exception as e:
					log("%s with sql %s" % (e, cmd), self, alarm.level.Critical)
					return
				if primary:
					cmd = "UPDATE `matrix`.`status` SET `input` = '{}',  `time` = CURRENT_TIMESTAMP WHERE `status`.`PRIMARY` ={};".format(
						source, primary)
				else:
					cmd = "INSERT INTO `matrix`.`status` (`PRIMARY`, `matrixid`, `input`, `output`, `levels`, `time`) VALUES (NULL, '{}', '{}', '{}', '{}', CURRENT_TIMESTAMP);".format(
						self.prefsDict["mtxId"], source, dest, lvl)
				self.qselect(cmd)
			self.db.commit()


class sharedSql(mysql):
	""" sql object is shared. Lock as well"""

	def __init__(self, name, db, sqlLock):

		self.name = name
		self.db = db
		self.sqlLock = sqlLock

		self.input = {}
		self.output = {}

	def dbConnect(self):
		with self.sqlLock:
			# noinspection PyBroadException
			try:
				self.db.ping()
			except Exception:
				self.set_offline("database")
