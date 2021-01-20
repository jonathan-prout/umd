from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from . import equipment
from . import gv
import random

def deserialize(data, keepData = True):
	""" Instanciates equip with data. Beware of keyerrors and Typeerrors"""
	equipTypes = {
		"GenericIRD":equipment.generic.GenericIRD,
		"TT1260":equipment.ericsson.TT1260,
		"RX1290":equipment.ericsson.RX1290,
		"DR5000":equipment.ateme.DR5000,
		"TVG420":equipment.tvips.TVG420,
		"IP GRIDPORT":equipment.omneon.IPGridport,
		"IP Gridport":equipment.omneon.IPGridport,
		"NS2000":equipment.novelsat.NS2000,
		"NS2000_WEB":equipment.novelsat.NS2000_WEB,
		"NS2000_SNMP":equipment.novelsat.NS2000_SNMP,
		"RX8200":equipment.ericsson.RX8200,
		"RX8200-4RF":equipment.ericsson.RX8200_4RF,
		"RX8200-2RF":equipment.ericsson.RX8200_2RF,
	}
	equip = equipTypes[data["modelType"] ](data["equipmentId"], data["ip"], data["name"])
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
	currentEquipment = deserialize(data)
	

	if not all( (gv.suppressEquipCheck, (not isinstance(currentEquipment, equipment.generic.GenericIRD ) ) ) ):
		try:
			equipTypeStr = currentEquipment.determine_type()
		except:
			equipTypeStr = "OFFLINE"
	equipmentID = currentEquipment.equipmentId
	ip = currentEquipment.ip
	
	name = currentEquipment.name
	# Equipment equipTypeStrs without subtype
	simpleTypes = {
		"TT1260":equipment.ericsson.TT1260,
		"RX1290":equipment.ericsson.RX1290,
		"DR5000":equipment.ateme.DR5000,
		"TVG420":equipment.tvips.TVG420,
		"IP GRIDPORT":equipment.omneon.IPGridport,
		"IP Gridport":equipment.omneon.IPGridport

	}
	
	
	for key in list(simpleTypes.keys()):
		if  any( ( (key in equipTypeStr), isinstance(currentEquipment, simpleTypes[key]) ) ):
			currentEquipment = simpleTypes[key](equipmentID, ip, name)
			#gv.addEquipment(currentEquipment)
			t = key
			break
		
	# Equipment equipTypeStr with subtype
	if any( ( ("Rx8000"in equipTypeStr), isinstance(currentEquipment, equipment.ericsson.RX8200) ) ):
		t = "Rx8200"
		currentEquipment = equipment.ericsson.RX8200(equipmentID, ip, name)
		subtype = currentEquipment.determine_subtype()
		if subtype == "RX8200-4RF":
			t = "Rx8200-4RF"
			currentEquipment = equipment.ericsson.RX8200_4RF(equipmentID, ip, name)
		elif subtype == "RX8200-2RF":
			t = "Rx8200-2RF"
			currentEquipment = equipment.ericsson.RX8200_2RF(equipmentID, ip, name)
		else:
			print("WARNING: id %d at %s not subtyped"%(equipmentID, ip))
		#gv.addEquipment(currentEquipment)
		
		
	elif  any( ( ("NS2000"in equipTypeStr), isinstance(currentEquipment, equipment.novelsat.NS2000) ) ):
		currentEquipment = equipment.novelsat.NS2000(equipmentID, ip, name)
		t = "NS2000"
		subtype = currentEquipment.determine_subtype()
		if subtype == "NS2000_WEB":
			t = subtype
			currentEquipment = equipment.novelsat.NS2000_WEB(equipmentID, ip, name)
		elif subtype == "NS2000_SNMP":
			currentEquipment = equipment.novelsat.NS2000_SNMP(equipmentID, ip, name)
			t = subtype
		#currentEquipment.lastRefreshTime = 0
		#currentEquipment.excpetedNextRefresh = float(random.randint(0,50)) /10
		#gv.addEquipment(currentEquipment)
		
		
	elif equipTypeStr == "OFFLINE":	
		t = "OFFLINE"
		currentEquipment.offline = True
	query = "UPDATE equipment SET model_id ='%s' WHERE id ='%i'"%(t, equipmentID)
	
	if gv.loud:
		print("IRD " + str(equipmentID) + " is a " + t)
	sendToSQL(query)
	u = 'Online'
	if t == 'OFFLINE':
	    u = 'Offline'
	query = "UPDATE `UMD`.`status` SET `aspectratio` = '',`status` = '%s', `ebno` = '', `frequency` = '', `symbolrate` = '', `asi` = '', `sat_input` = '', `castatus` = '', `videoresolution` = '', `framerate` = '', `videostate` = '', `asioutencrypted` = '', `framerate` = '',`muxbitrate` = '', `muxstate` = '' WHERE `status`.`id` = '%i'"%(u, equipmentID)
	sendToSQL(query)
	checkin(currentEquipment.serialize())


def refresh(data):
	currentEquipment = deserialize(data)
	#print "refresh method"
	#print "deserialized %s: %s"%(currentEquipment.equipmentId,currentEquipment.modelType )
	try:
		currentEquipment.refresh()
	except:
		currentEquipment.set_offline()
	
	if not currentEquipment.get_offline():		    
		
		updatesql = currentEquipment.updatesql()
		sendToSQL(updatesql)

		updatechannel = currentEquipment.getChannel()
		sendToSQL(updatechannel)
		
	
		"""
		try:
			
			currentEquipment.refreshjitter = time.time() - currentEquipment.excpetedNextRefresh 
		except: pass
		
		
		currentEquipment.excpetedNextRefresh = time.time() + currentEquipment.min_refresh_time()
		"""
		# Add itself to end of queue
		checkin(currentEquipment.serialize())
	else:
		updatesql = "UPDATE `UMD`.`status` SET `aspectratio` = '',`status` = 'Offline', `ebno` = '', `frequency` = '', `symbolrate` = '', `asi` = '', `sat_input` = '', `castatus` = '', `videoresolution` = '', `framerate` = '', `videostate` = '', `asioutencrypted` = '', `framerate` = '',`muxbitrate` = '', `muxstate` = '' WHERE `status`.`id` = '%i'"%currentEquipment.equipmentId
		sendToSQL(updatesql)
		checkin(currentEquipment.serialize())
	#print "end refresh method"
	
funcs = {"determine_type":determine_type,
		 "refresh":refresh}