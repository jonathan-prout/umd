
def determine_type(args):
	t = "ERROR"
	equipTypeStr = "OFFLINE"
	equipmentID, autostart = args
	gv.statDict[equipmentID] = {"determined":"undetermined","last action":"determine type", "timestamp":time.time()}
	try: #remove from offline equip list if it's in there
		gv.offlineEquip.remove(equipmentID)
	except ValueError:
		pass
	if not all( (gv.suppressEquipCheck, (not isinstance(gv.equipmentDict[equipmentID], equipment.generic.GenericIRD ) ) ) ):
		try:
			equipTypeStr = gv.equipmentDict[equipmentID].determine_type()
		except:
			equipTypeStr = "OFFLINE"
	
	ip = gv.equipmentDict[equipmentID].ip
	
	name = gv.equipmentDict[equipmentID].name
	# Equipment equipTypeStrs without subtype
	simpleTypes = {
		"TT1260":equipment.ericsson.TT1260,
		"RX1290":equipment.ericsson.RX1290,
		"DR5000":equipment.ateme.DR5000,
		"TVG420":equipment.tvips.TVG420,
		"IP Gridport":equipment.omneon.IPGridport
		
	}
		
	
	for key in simpleTypes.keys():
		if  any( ( (key in equipTypeStr), isinstance(gv.equipmentDict[equipmentID], simpleTypes[key]) ) ):
			newird = simpleTypes[key](equipmentID, ip, name)
			newird.lastRefreshTime = 0
			newird.excpetedNextRefresh = float(random.randint(0,50)) /10
			gv.addEquipment(newird)
			t = key
			break
		
	# Equipment equipTypeStr with subtype
	if any( ( ("Rx8000"in equipTypeStr), isinstance(gv.equipmentDict[equipmentID], equipment.ericsson.RX8200) ) ):
		newird = equipment.ericsson.RX8200(equipmentID, ip, name)
		subtype = newird.determine_subtype()
		if subtype == "RX8200-4RF":
		    newird = equipment.ericsson.RX8200_4RF(equipmentID, ip, name)
		elif subtype == "RX8200-2RF":
		    newird = equipment.ericsson.RX8200_2RF(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		newird.excpetedNextRefresh = float(random.randint(0,50)) /10
		gv.addEquipment(newird)
		t = "Rx8200"
		
	elif  any( ( ("NS2000"in equipTypeStr), isinstance(gv.equipmentDict[equipmentID], equipment.novelsat.NS2000) ) ):
		newird = equipment.novelsat.NS2000(equipmentID, ip, name)
		subtype = newird.determine_subtype()
		if subtype == "NS2000_WEB":
		    newird = equipment.novelsat.NS2000_WEB(equipmentID, ip, name)
		elif subtype == "NS2000_SNMP":
		    newird = equipment.novelsat.NS2000_SNMP(equipmentID, ip, name)
		newird.lastRefreshTime = 0
		newird.excpetedNextRefresh = float(random.randint(0,50)) /10
		gv.addEquipment(newird)
		t = "NS2000"
		
	elif equipTypeStr == "OFFLINE":	
		t = "OFFLINE"
		gv.equipmentDict[equipmentID].offline = True
	query = "UPDATE equipment SET model_id ='%s' WHERE id ='%i'"%(t, equipmentID)
	
	if gv.loud:
		print "IRD " + str(equipmentID) + " is a " + t
	gv.dbQ.put(query)
	u = 'Online'
	if t == 'OFFLINE':
	    u = 'Offline'
	query = "UPDATE `UMD`.`status` SET `aspectratio` = '',`status` = '%s', `ebno` = '', `frequency` = '', `symbolrate` = '', `asi` = '', `sat_input` = '', `castatus` = '', `videoresolution` = '', `framerate` = '', `videostate` = '', `asioutencrypted` = '', `framerate` = '',`muxbitrate` = '', `muxstate` = '' WHERE `status`.`id` = '%i'"%(u, equipmentID)
	gv.dbQ.put(query)
	gv.sqlUpdateDict[equipmentID] = time.time()
	if autostart:
		if gv.threadJoinFlag == False:
			if equipTypeStr != "OFFLINE":
				gv.statDict[equipmentID]["last action"]= "checkin"
				gv.statDict[equipmentID]["timestamp"] = time.time()
				gv.ThreadCommandQueue.put((refresh, equipmentID))

def refresh(equipmentID):
	currentEquipment = gv.equipmentDict[equipmentID]
	import time
	gv.statDict[equipmentID]["last action"]= "checkout"
	gv.statDict[equipmentID]["timestamp"] = time.time()
	try:
		t = currentEquipment.excpetedNextRefresh
	except:
		t = 0
	
	if not currentEquipment.get_offline():
		if t > time.time():
			#if gv.loud: print "sleeping %s seconds" % max(0, (gv.min_refresh_time - (time.time() - t) ))
			#sleepytime = min(max(0, (currentEquipment.min_refresh_time() - (time.time() - t) )), 1)
			if gv.threadJoinFlag == False:
				gv.ThreadCommandQueue.put((refresh, equipmentID))
				gv.statDict[equipmentID]["last action"]= "checkin"
				gv.statDict[equipmentID]["timestamp"] = time.time()
			sleepytime = 0.1
			time.sleep(sleepytime)
			return 
		
	try:
		currentEquipment.refresh()
	except:
		currentEquipment.set_offline()
	
	if not currentEquipment.get_offline():		    
		
		updatesql = currentEquipment.updatesql()
		gv.dbQ.put(updatesql)
		gv.sqlUpdateDict[equipmentID] = time.time()
		msg = None # not needed i think
		#except: raise "gv.sql ERRROR"
		
		# process channel
		updatechannel = currentEquipment.getChannel()
		gv.dbQ.put(updatechannel)
		gv.sqlUpdateDict[equipmentID] = time.time()
		re = None# not needed i think
		currentEquipment.lastRefreshTime = time.time()
		try:
			
			currentEquipment.refreshjitter = time.time() - currentEquipment.excpetedNextRefresh 
		except: pass
		
		
		currentEquipment.excpetedNextRefresh = time.time() + currentEquipment.min_refresh_time()
		gv.hit(equipmentID)
		# Add itself to end of queue
		if gv.threadJoinFlag == False:
			gv.ThreadCommandQueue.put((refresh, equipmentID))
			gv.statDict[equipmentID]["last action"]= "checkin"
			gv.statDict[equipmentID]["timestamp"] = time.time()
	else:
		updatesql = "UPDATE `UMD`.`status` SET `aspectratio` = '',`status` = 'Offline', `ebno` = '', `frequency` = '', `symbolrate` = '', `asi` = '', `sat_input` = '', `castatus` = '', `videoresolution` = '', `framerate` = '', `videostate` = '', `asioutencrypted` = '', `framerate` = '',`muxbitrate` = '', `muxstate` = '' WHERE `status`.`id` = '%i'"%equipmentID
		gv.dbQ.put(updatesql)
		gv.sqlUpdateDict[equipmentID] = time.time()
	