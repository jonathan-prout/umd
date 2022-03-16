from __future__ import print_function
from __future__ import absolute_import
from future import standard_library

from helpers import alarm, processing
from helpers.logging import log

standard_library.install_aliases()
from builtins import str
import sys
import traceback
import threading
from pysnmp.proto import rfc1902

import subprocess

from pysnmp.entity.rfc3413.oneliner import cmdgen


class NetSNMPTimedOut(Exception):
	def __init__(self, msg):
		self.msg = msg

	def __str__(self):
		return "NetSNMPTimedOut with %s" % self.msg


class NetSNMPUnknownOID(Exception):
	failedOid = None

	def __init__(self, msg):
		self.msg = msg

	def __str__(self):
		return "NetSNMPUnknownOID with %s" % self.msg


class NetSNMPTooBig(Exception):
	failedOid = None

	def __init__(self, msg):
		self.msg = msg

	def __str__(self):
		return "NetSNMPTooBig with %s" % self.msg


def handle_netSNMP_error(serr):
	if "Timeout:" in serr:
		raise NetSNMPTimedOut(serr)
	elif 'Reason: (noSuchName) There is no such variable name in this MIB.' in serr:
		failedOid = None
		try:
			"""Failed object: iso.3.6.1.4.1.37576.2.3.1.5.1.2.1"""
			line = serr.split("\n")[2]
			line = line.replace("Failed object: ", "")
			line = line.replace("iso", "")
			failedOid = line.strip()

		except:
			pass
		e = NetSNMPUnknownOID(serr)
		e.failedOid = failedOid
		raise e
	elif 'Reason: (tooBig) Response message would have been too large.' in serr:
		failedOid = None
		try:
			"""Failed object: iso.3.6.1.4.1.37576.2.3.1.5.1.2.1"""
			line = serr.split("\n")[2]
			line = line.replace("Failed object: ", "")
			line = line.replace("iso", "")
			failedOid = line.strip()

		except:
			pass
		e = NetSNMPTooBig(serr)
		e.failedOid = failedOid
		raise e


def get_pysnmp_instance():
	t = threading.currentThread()
	try:
		return t.pysnmp_instance
	except AttributeError:
		t.pysnmp_instance = cmdgen.CommandGenerator()
		return t.pysnmp_instance


def oidFromDict(n, invdict):
	if n not in invdict:
		if "." + n in invdict:
			n = "." + n
		else:

			for k, v in list(invdict.items()):
				if n in k:
					n = k
	return n


def get(commandDict, ip):
	# import gv
	return get_subprocess(commandDict, ip)
	"""
	try:
		return get_subprocess(commandDict, ip)
	
	except NetSNMPTimedOut:
		return {}
	except Exception as e:
	"""
	"""
		if any( ( isinstance(e, AssertionError), isinstance(e, AttributeError) ) ):
			if gv.loudSNMP:
				print "NETSNP Errored so using PYSNMP on %s"% ip
			return get_pysnmp(commandDict, ip)
		else:
			print "snmp.get: %s Error on %s"% (type(e),ip)
			gv.exceptions.append((e, traceback.format_tb( sys.exc_info()[2]) ))
			raise e
		"""
	"""
		raise e
	"""


def get_pysnmp(commandDict, ip):
	# import gv
	if commandDict == {}:
		return {}
	commands = []
	invdict = {}
	returndict = {}
	for k, v in list(commandDict.items()):
		v = v.replace('enterprises.', '.1.3.6.1.4.1.')
		v = v.replace(' ', '')  # no spaces
		commands.append(v)
		invdict[v] = k
	errorIndication, errorStatus, errorIndex, varBinds = get_pysnmp_instance().getCmd(
		cmdgen.CommunityData('my-agent', 'public', 0), cmdgen.UdpTransportTarget((ip, 161)), *commands)
	if errorStatus:
		log("SNMP ERROR for %s. errorIndication: %s errorStatus: %s errorIndex: %s"%(ip, errorIndication, errorStatus, errorIndex),
			f"snmp.get_pysnmp on {ip}", alarm.level.Warining)

		x = errorIndex - 1

		log(" %s: %s" % (x + 1, varBinds[x]))
		try:
			n = oidFromDict(str(varBinds[x][0]), invdict)

		except ValueError as e:
			log(f"ValueError {e} when determining what to remove" f"snmp.get_pysnmp on {ip}", alarm.level.Major)

		# try:
		if invdict[n] in commandDict:
			log("Removing %s for %s and trying again" % (k, ip), f"snmp.get_pysnmp on {ip}", alarm.level.Info)
			del commandDict[invdict[n]]
			return get(commandDict, ip)  # Call itself
		else:
			return {}
	else:
		for item in varBinds:

			n = oidFromDict(str(item[0]), invdict)
			try:
				if isinstance(v, rfc1902.Integer):
					returndict[invdict[n]] = int(item[1])
				elif isinstance(v, rfc1902.Integer32):
					returndict[invdict[n]] = int(item[1])
				elif isinstance(v, rfc1902.OctetString):
					returndict[invdict[n]] = str(item[1])
				else:
					returndict[invdict[n]] = str(item[1])
			except KeyError:
				log(f"KeyError in mapping dict {invdict}, {oid}={value}", f"snmp.get_pysnmp on {ip}", alarm.level.Warning)
	del errorIndication
	del errorStatus
	del errorIndex
	del varBinds
	return returndict


def process_netsnmp_line(outputLine):
	oid, p2 = outputLine.split("=")
	s = p2.split(":")
	valtype = s[0]
	value = ":".join(s[1:])
	oid = oid.replace("iso", ".1")
	oid = oid.replace(" ", "")

	# format result

	if valtype.strip() == "INTEGER":
		value = int(value)
	elif valtype.strip() == "STRING":
		value = value.replace('"', '').strip()
	else:
		try:
			s = value.split('"')[1]  # ie  " +05.3 dB"
			assert (len(s) == 3)
			value = s[1]

		except:
			pass
	return oid, valtype, value


def get_subprocess(commandDict, ip):
	""" Uses subporcess.popen to getch snmp rather than PYSNMP """

	# import gv
	if commandDict == {}:
		return {}
	commands = []
	invdict = {}
	returndict = {}
	for k, v in list(commandDict.items()):
		v = v.replace('enterprises.', '.1.3.6.1.4.1.')
		v = v.replace(' ', '')  # no spaces
		commands.append(v)
		invdict[v] = k

	supressErrors = []
	returncode = 0

	try:
		sub = subprocess.Popen(["/usr/bin/snmpget", "-v1", "-cpublic", ip] + commands, stdout=subprocess.PIPE,
		                       stderr=subprocess.PIPE, close_fds=True)
	# sout = subprocess.check_output(["/usr/bin/snmpget", "-v1", "-cpublic", ip] + commands, stderr=subprocess.STDOUT)

	except subprocess.CalledProcessError as e:
		returncode = 1

	returncode = sub.wait()  # Block here waiting for subprocess to return. Next thrad should execute from here
	sout = sub.stdout.read().decode("UTF-8")
	try:
		serr = sub.stderr.read().decode("UTF-8")
	except (EOFError, TypeError, AttributeError):
		serr = ""
	del sub
	if returncode != 0:
		try:
			handle_netSNMP_error(serr)
		except NetSNMPUnknownOID as e:
			if e.failedOid:
				for k in list(commandDict.keys()):
					if commandDict[k] == e.failedOid:
						log("Removing %s for %s and trying again" % (k, ip), f"snmp.get_subprocesss on {ip}", alarm.level.Info)
						del commandDict[k]
						return get(commandDict, ip)  # Call itself

	assert (
				returncode == 0)  # Error if NET SNMP has an error. Fall back to PYSNMP which is slower but with better error handling
	for outputLine in sout.split('\n'):
		try:
			oid, valtype, value = process_netsnmp_line(outputLine)
			n = oidFromDict(oid, invdict)
		except ValueError:
			continue
		try:
			# returndict[invdict[ n ] ] = str(value) #To be checked
			returndict[invdict[n]] = value
		except KeyError:
			log(f"KeyError in mapping dict {invdict}, {oid}={value}", f"snmp.get_subprocesss on {ip}", alarm.level.Warning)

	return returndict


def walk(commandDict, ip):
	# import gv

	try:
		return walk_subprocess(commandDict, ip)
	except Exception as e:
		"""
		if isinstance(e, AssertionError):
			if gv.loudSNMP:
				print "NETSNP WALK Errored so using PYSNMP on %s"% ip
				return walk_pysnmp(commandDict, ip)
		else:
			print "snmp.walk: %s Error on %s"% (type(e),ip)
		"""
		raise e


def getbulk(commandDict, ip, numItems):
	try:
		return getbulk_subprocess(commandDict, ip, numItems)
	except NetSNMPTooBig:
		return walk(commandDict, ip)
	except NetSNMPTimedOut:
		return {}
	except NetSNMPUnknownOID as e:
		if e.failedOid:
			for k in list(commandDict.keys()):
				if commandDict[k] == e.failedOid:
					log("Removing %s for %s and trying again" % (k, ip), f"snmp.getbulk on {ip}", alarm.level.Info)
					del commandDict[k]
					return getbulk(commandDict, ip, numItems)  # Call itself

	except Exception as e:
		"""
		if isinstance(e, AssertionError):
			if gv.loudSNMP:
				print "NETSNP GETBULK Errored so using PYSNMP on %s"% ip
				return walk_pysnmp(commandDict, ip)
		else:
			print "snmp.getbulk: %s Error on %s"% (type(e),ip)
		"""
		raise e


def getbulk_subprocess(commandDict, ip, numItems):
	""" Uses subporcess.popen to getch snmp rather than PYSNMP """

	# import gv
	if commandDict == {}:
		return {}
	commands = []
	invdict = {}
	returndict = {}
	for k, v in list(commandDict.items()):
		v = v.replace('enterprises.', '.1.3.6.1.4.1.')
		v = v.replace(' ', '')  # no spaces
		commands.append(v)
		invdict[v] = k
	for command in commands:
		sub = subprocess.Popen(["/usr/bin/snmpbulkget", "-v2c", "-Of", "-cpublic", "-Cr%d" % numItems, ip, command],
		                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
		# /usr/bin/snmpbulkget -cpublic -v2c -Of -Cr3 192.168.1.111 .1.3.6.1.4.1.27338.5.5.1.5.1.1.9

		returncode = sub.wait()  # Block here waiting for subprocess to return. Next thrad should execute from here
		sout = sub.stdout.read()
		try:
			serr = processing.decodeUTF8(sub.stderr.read())
		except (ValueError, EOFError, TypeError, AttributeError):
			serr = ""
		try:
			sout = processing.decodeUTF8(sout)
		except (ValueError, TypeError):
			pass

		if returncode != 0:
			log(f"returncode {returncode}", f"getbulk_subprocess {ip}", alarm.level.Warning)
			log(f"stdout {sout}", f"getbulk_subprocess {ip}", alarm.level.Warning)
			log(f"stderr {serr}", f"getbulk_subprocess {ip}", alarm.level.Warning)
		del sub

		if serr:
			handle_netSNMP_error(serr)

		assert (
					returncode == 0)  # Error if NET SNMP has an error. Fall back to PYSNMP which is slower but with better error handling
		results = []
		for outputLine in sout.split("\n"):
			try:
				oid, valtype, value = process_netsnmp_line(outputLine)
				results.append(value)
			except ValueError:
				continue
		n = oidFromDict(command, invdict)
		returndict[invdict[n]] = results
	return returndict


def walk_subprocess(commandDict, ip):
	""" Uses subporcess.popen to getch snmp rather than PYSNMP """

	# import gv
	if commandDict == {}:
		return {}
	commands = []
	invdict = {}
	returndict = {}
	for k, v in list(commandDict.items()):
		v = v.replace('enterprises.', '.1.3.6.1.4.1.')
		v = v.replace(' ', '')  # no spaces
		commands.append(v)
		invdict[v] = k
	for command in commands:
		sub = subprocess.Popen(["/usr/bin/snmpwalk", "-v1", "-cpublic", ip, command], stdout=subprocess.PIPE)
		returncode = sub.wait()  # Block here waiting for subprocess to return. Next thrad should execute from here
		sout = sub.stdout.read()
		try:
			serr = processing.decodeUTF8(sub.stderr.read())
		except (ValueError, EOFError, TypeError, AttributeError):
			serr = ""
		try:
			sout = processing.decodeUTF8(sout)
		except (ValueError, TypeError):
			pass
		if returncode != 0:
			log(f"returncode {returncode}", f"walk_subprocess {ip}", alarm.level.Warning)
			log(f"stdout {sout}", f"walk_subprocess {ip}", alarm.level.Warning)
			log(f"stderr {serr}", f"walk_subprocess {ip}", alarm.level.Warning)
		del sub
		assert (
					returncode == 0)  # Error if NET SNMP has an error. Fall back to PYSNMP which is slower but with better error handling
		results = []
		for outputLine in sout.split("\n"):
			try:
				oid, valtype, value = process_netsnmp_line(outputLine)
				results.append(value)
			except ValueError:
				continue
		n = oidFromDict(command, invdict)
		if results:
			returndict[invdict[n]] = results
	return returndict


def walk_pysnmp(commandDict, ip):
	commands = []
	invdict = {}
	returndict = {}
	for k, v in list(commandDict.items()):
		v = v.replace('enterprises.', '.1.3.6.1.4.1.')
		commands.append(v)
		invdict[v] = k
	for command in commands:
		errorIndication, errorStatus, errorIndex, varBindsTable = get_pysnmp_instance().nextCmd(
			cmdgen.CommunityData('my-agent', 'public', 0), cmdgen.UdpTransportTarget((ip, 161)),
			command
		)
		results = []
		if errorStatus:
			for x in [errorIndication, errorStatus, errorIndex, varBindsTable]:
				log(x, f"walk_pysnmp {ip}", alarm.level.Warning)

		else:
			for item in varBindsTable:
				try:
					item = item[0][1]
				except:
					item = item[0]
				results.append(str(item))
		n = oidFromDict(command, invdict)
		returndict[invdict[n]] = results
	return returndict
