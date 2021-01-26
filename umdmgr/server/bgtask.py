from __future__ import print_function
from __future__ import absolute_import
from builtins import str

from server import gv
import random

import server.equipment.generic
import server.equipment.ericsson
import server.equipment.ateme
import server.equipment.tvips
import server.equipment.omneon
import server.equipment.novelsat

from helpers import logging
from helpers import alarm

def deserialize(data, keepData=True):
	""" Instantiates equip with data. Beware of KeyError and TypeError"""
	equipTypes = {
		"GenericIRD": server.equipment.generic.GenericIRD,
		"TT1260": server.equipment.ericsson.TT1260,
		"RX1290": server.equipment.ericsson.RX1290,
		"DR5000": server.equipment.ateme.DR5000,
		"TVG420": server.equipment.tvips.TVG420,
		"IP GRIDPORT": server.equipment.omneon.IPGridport,
		"IP Gridport": server.equipment.omneon.IPGridport,
		"NS2000": server.equipment.novelsat.NS2000,
		"NS2000_WEB": server.equipment.novelsat.NS2000_WEB,
		"NS2000_SNMP": server.equipment.novelsat.NS2000_SNMP,
		"RX8200": server.equipment.ericsson.RX8200,
		"RX8200-4RF": server.equipment.ericsson.RX8200_4RF,
		"RX8200-2RF": server.equipment.ericsson.RX8200_2RF,
	}
	equip = equipTypes[data["modelType"]](data["equipmentId"], data["ip"], data["name"])
	if keepData:
		equip.deserialize(data)
	return equip


def checkin(data):
	gv.CheckInQueue.put(data)


def sendToSQL(query):
	gv.dbQ.put(query)


def determine_type(data):
	t = "ERROR"
	equipTypeStr = "OFFLINE"
	current_equipment = deserialize(data)

	if not all((gv.suppressEquipCheck, (not isinstance(current_equipment, server.equipment.generic.GenericIRD)))):
		try:
			equipTypeStr = current_equipment.determine_type()
		except:
			equipTypeStr = "OFFLINE"
	equipmentID = current_equipment.equipmentId
	ip = current_equipment.ip

	name = current_equipment.name
	# Equipment equipTypeStrs without subtype
	simpleTypes = {
		"TT1260": server.equipment.ericsson.TT1260,
		"RX1290": server.equipment.ericsson.RX1290,
		"DR5000": server.equipment.ateme.DR5000,
		"TVG420": server.equipment.tvips.TVG420,
		"IP GRIDPORT": server.equipment.omneon.IPGridport,
		"IP Gridport": server.equipment.omneon.IPGridport

	}

	for key in list(simpleTypes.keys()):
		if any(((key in equipTypeStr), isinstance(current_equipment, simpleTypes[key]))):
			current_equipment = simpleTypes[key](equipmentID, ip, name)
			# gv.addEquipment(current_equipment)
			t = key
			break

	# Equipment equipTypeStr with subtype
	if any((("Rx8000" in equipTypeStr), isinstance(current_equipment, server.equipment.ericsson.RX8200))):
		t = "Rx8200"
		current_equipment = server.equipment.ericsson.RX8200(equipmentID, ip, name)
		subtype = current_equipment.determine_subtype()
		if subtype == "RX8200-4RF":
			t = "Rx8200-4RF"
			current_equipment = server.equipment.ericsson.RX8200_4RF(equipmentID, ip, name)
		elif subtype == "RX8200-2RF":
			t = "Rx8200-2RF"
			current_equipment = server.equipment.ericsson.RX8200_2RF(equipmentID, ip, name)
		else:
			print("WARNING: id %d at %s not subtyped" % (equipmentID, ip))
	# gv.addEquipment(current_equipment)


	elif any((("NS2000" in equipTypeStr), isinstance(current_equipment, server.equipment.novelsat.NS2000))):
		current_equipment = server.equipment.novelsat.NS2000(equipmentID, ip, name)
		t = "NS2000"
		subtype = current_equipment.determine_subtype()
		if subtype == "NS2000_WEB":
			t = subtype
			current_equipment = server.equipment.novelsat.NS2000_WEB(equipmentID, ip, name)
		elif subtype == "NS2000_SNMP":
			current_equipment = server.equipment.novelsat.NS2000_SNMP(equipmentID, ip, name)
			t = subtype
	# current_equipment.lastRefreshTime = 0
	# current_equipment.excpetedNextRefresh = float(random.randint(0,50)) /10
	# gv.addEquipment(current_equipment)


	elif equipTypeStr == "OFFLINE":
		t = "OFFLINE"
		current_equipment.offline = True
	query = "UPDATE equipment SET model_id ='%s' WHERE id ='%i'" % (t, equipmentID)

	if gv.loud:
		print("IRD " + str(equipmentID) + " is a " + t)
	sendToSQL(query)
	u = 'Online'
	if t == 'OFFLINE':
		u = 'Offline'
	query = "UPDATE `UMD`.`status` SET `aspectratio` = '',`status` = '%s', `ebno` = '', `frequency` = '', `symbolrate` = '', `asi` = '', `sat_input` = '0', `castatus` = '', `videoresolution` = '', `framerate` = '', `videostate` = '', `asioutencrypted` = '', `framerate` = '',`muxbitrate` = '', `muxstate` = '' WHERE `status`.`id` = '%i'" % (
	u, equipmentID)
	sendToSQL(query)
	checkin(current_equipment.serialize())


def refresh(data):
	current_equipment = deserialize(data)
	# print "refresh method"
	# print "deserialized %s: %s"%(current_equipment.equipmentId,current_equipment.modelType )
	try:
		current_equipment.refresh()
	except Exception as e:
		logging.logerr(current_equipment)
		current_equipment.set_offline(f"Exception {e} caught in refresh")

	if not current_equipment.get_offline():

		updatesql = current_equipment.updatesql()
		sendToSQL(updatesql)

		updatechannel = current_equipment.getChannel()
		sendToSQL(updatechannel)

		"""
		try:
			
			current_equipment.refreshjitter = time.time() - current_equipment.excpetedNextRefresh 
		except: pass
		
		
		current_equipment.excpetedNextRefresh = time.time() + current_equipment.min_refresh_time()
		"""
		# Add itself to end of queue
		checkin(current_equipment.serialize())
	else:
		updatesql = "UPDATE `UMD`.`status` SET `aspectratio` = '',`status` = 'Offline', `ebno` = '', `frequency` = '', `symbolrate` = '', `asi` = '', `sat_input` = '0', `castatus` = '', `videoresolution` = '', `framerate` = '', `videostate` = '', `asioutencrypted` = '', `framerate` = '',`muxbitrate` = '', `muxstate` = '' WHERE `status`.`id` = '%i'" % current_equipment.equipmentId
		sendToSQL(updatesql)
		checkin(current_equipment.serialize())


# print "end refresh method"

funcs = {"determine_type": determine_type,
         "refresh": refresh}
