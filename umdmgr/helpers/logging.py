from __future__ import absolute_import
from __future__ import print_function
from builtins import range
from builtins import str
from builtins import object

'''
Created on 1 avr. 2016

@author: prout
'''

import time

import helpers.alarm 

import os
import traceback, sys, string
import threading
import time

DEBUG_NONE	= 0
DEBUG_ALL	= 1
DEBUG_STDOUT = 2
DEBUG_FILE = 4

debug = DEBUG_ALL
""" Project Headers """

logLock = threading.Lock()
ioLock = True
debugLock = threading.Lock()
MIN_SEVERITY = helpers.alarm.level.OK
import logging
import logging.handlers
import colorlog
from pythonjsonlogger import jsonlogger
# create logger

pylog_level = {	}

for lvl in range(len(helpers.alarm._levels)):
	""" levels should be positive integers and they should increase in increasing order of severity."""
	levelName = helpers.alarm._levels[lvl]
	levelValue = 60 + len(helpers.alarm._levels)- lvl
	pylog_level[lvl] = levelValue
	logging.addLevelName(levelValue, levelName)
	setattr(logging, levelName, levelValue)
	

logger = logging.getLogger('matrix')
#logger.setLevel(logging.DEBUG)

#Console output

#consolelog.setLevel(logging.DEBUG)


logcolour = {

"Emergency"			:"red",
"Critical"			 :"red,bg_white",
"Error"				:"red",
"Major"				:"red",
"Minor"				:"yellow",
"Warning"			  :"yellow",
"Indeterminate"		:"purple",
"Notice"			   :"purple",
"Info"				 :"blue,bg_white",
"Cleared"			  :"cyan",
"Debug"				:"cyan",
"Redundant"			:"green",
"OK"				   :"green",
}


def addColourLog(logger):
	consolelog = colorlog.StreamHandler()
	consolelog.setLevel(logging.DEBUG)
	formatter  = colorlog.ColoredFormatter(
		"%(asctime)s: %(log_color)s[%(levelname)-8s]%(reset)s %(white)s[%(callingInstance)s] %(message)s",
		datefmt=None,
		reset=True,
		log_colors=logcolour,
		secondary_log_colors={},
		style='%'
	)
	
	consolelog.setFormatter(formatter)
	logger.addHandler(consolelog)


def addStreamLogger(logger):
	consolelog = logging.StreamHandler()
	consolelog.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s[%(levelname)s][%(callingInstance)s] %(message)s')
	consolelog.setFormatter(formatter)
	logger.addHandler(consolelog)

def addJSONLog(logger):
	logHandler = logging.StreamHandler()
	fields = ['asctime', "message", "process", "callingInstance", "threadName", "levelname"]
	formatter = jsonlogger.JsonFormatter(" ".join("({})".format(s) for s in fields))
	logHandler.setFormatter(formatter)
	logger.addHandler(logHandler)


def removeAllHandlers(logger):
	while 1:
		try:
			logger.removeHandler(logger.handlers[0])
		except IndexError:
			return


def addFileLogger(logger, filename):
	filelogger = logging.handlers.TimedRotatingFileHandler(filename, when="midnight", backupCount=30)
	logging.handlers.RotatingFileHandler.doRollover(filelogger)
	filelogger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(callingInstance)s;%(message)s')
	filelogger.setFormatter(formatter)
	logger.addHandler(filelogger)
	
def syncDebug(s):
	debugLock.acquire()
	if debug == DEBUG_NONE:
		pass
	elif debug == DEBUG_ALL:
		print(s)
	elif debug == DEBUG_STDOUT:
		print(s)
	elif debug == DEBUG_FILE:
		try:
			with open(gv.debugFile, "a") as l:
					l.write("%s: %s\r\n"%(time.strftime("%Y %m %d %H:%M:%S"), s))
		except IOError:
			print ("Error with logging process. Cannot write to %s"%gv.debugFile)
	
	
	
	debugLock.release()

class severityAdapter(logging.LoggerAdapter):
	"""
	This adapter expects the passed in dict-like object to have a
	'severity' key, whose value in brackets is prepended to the log message.
	"""
	def process(self, msg, kwargs):
		return '[%s]%s' % (self.extra['seberity'], msg), kwargs


def basic_print_log(message, callingInstance=None, severity= helpers.alarm.level.Debug):
	if severity > MIN_SEVERITY:
		return
	print("{0}:[{1}][{2}]{3}".format(  time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
		  helpers.alarm.to_string(severity),
		  str(callingInstance), 
		  message
		  ))

def basic_logfile_log(message, callingInstance=None, severity= helpers.alarm.level.Debug):
	if severity > MIN_SEVERITY:
		return
	msg = "{0}:[{1}][{2}]{3}".format(  time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
		  helpers.alarm.to_string(severity),
		  str(callingInstance), 
		  message
		  )
	print(msg)
	with open(bagels.runtimeVariables.config.get("log_dir", "/var/log/bagels")+os.sep+str(callingInstance)+".log", "a") as fobj:
		fobj.write(msg +"\r\n")
		



def pylogging_log(message, callingInstance=None, severity= helpers.alarm.level.Debug):
	if severity > MIN_SEVERITY:
		return
	#msg = "[{0}] {1}".format(
	#		  str(callingInstance), 
	#		  message)
	logger.log(level = pylog_level[severity], msg = message, extra = {"callingInstance":str(callingInstance)})
	

log = pylogging_log

fileLogFormatter = logging.Formatter('%(asctime)s;%(levelname)s;%(callingInstance)s;%(message)s')


class list_handler(logging.Handler):
	def __init__(self, *args, list_length = 1000, **kwargs):
		logging.Handler.__init__(self, *args, **kwargs)
		self._list_length = list_length
		self.lock = threading.RLock()
		self._list = []
	
	def emit(self, record):
		"""Add the formatted log message (without newlines) to the list."""
		with self.lock:
			self._list.append(self.format(record).rstrip('\n'))
			while len(self._list) > self._list_length:
				self._list = self._list[1:]

class log_mixin(object):
	def log(self, message, severity = helpers.alarm.level.Info):
		log(message, self, severity)
	def debug(self, message, severity = helpers.alarm.level.Debug):
		log(message, self, severity)

taskLoggers = {}
taskConsoleLoggerLevel = logging.DEBUG
def createTaskLogger(uid):
	if uid not in taskLoggers:
		taskLoggers[uid] = _createTaskLogger(uid)
	return taskLoggers.get(uid)
	
def _createTaskLogger(uid):
	newLog = logging.getLogger(uid)
	newLog.setLevel(taskConsoleLoggerLevel)
	if bagels.runtimeVariables.config.get("logFormat", "default") =="colour":
		addColourLog(newLog)
	elif bagels.runtimeVariables.config.get("logFormat", "default").upper() =="JSON":
		addJSONLog(newLog)
	else:
		addStreamLogger(newLog)
		
	logdir = bagels.runtimeVariables.config.get("logdir")
	newfilelogger = logging.FileHandler(logdir + os.sep +"task_{}.log".format(uid))
	
	newfilelogger.setLevel(logging.DEBUG)
	
	newfilelogger.setFormatter(fileLogFormatter)
	newLog.addHandler(newfilelogger)
	return newLog
	
	
def logerr(callingInstance = "", severity = helpers.alarm.level.Critical, logger = log):
	limit = None
	_type, value, tb = sys.exc_info(  )
	_list = traceback.format_tb(tb, limit) + traceback.format_exception_only(_type, value)
	body = "Traceback (innermost last):\n" + "%-20s %s" % (
		",".join(_list[:-1], ), _list[-1] )
	
	logger(body, callingInstance, severity)


def startlogging(filename):
	removeAllHandlers(helpers.logging.logger)
	addColourLog(helpers.logging.logger)
	addFileLogger(helpers.logging.logger, filename)
	log("Started Logging", "Start", helpers.alarm.level.OK)

