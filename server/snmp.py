def oidFromDict(n , invdict):
	if not invdict.has_key(n):
		if invdict.has_key("." + n):
			n = "." + n
		else:
			for k, v in invdict:
				if n in k:
					n = k
	return n
	
def get(commandDict, ip):
	from pysnmp.entity.rfc3413.oneliner import cmdgen
	import gv
	if commandDict == {}:
		return {}
	commands = []
	invdict = {}
	returndict = {}
	for k,v in commandDict.items():
		v = v.replace('enterprises.','.1.3.6.1.4.1.')
		v = v.replace(' ', '' ) #no spaces
		commands.append(v)
		invdict[v] = k
	errorIndication, errorStatus, errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
	cmdgen.CommunityData('my-agent', 'public', 0), cmdgen.UdpTransportTarget((ip, 161)),
	*commands
	)
	if errorStatus:
		if gv.loud:
			print "SNMP ERROR for %s" %  ip
			print "errorIndication: %s" % errorIndication
			print "errorStatus: %s" % errorStatus
			print "errorIndex: %s" % errorIndex,
		x = errorIndex -1
		if gv.loud:
			print " %s: %s" % (x+1,varBinds[x])
		try:
			n = oidFromDict(str(varBinds[x][0] ), invdict )
			#print invdict[n]
		except ValueError:
			
			print "not in dict"
			print invdict
		#try:
		if commandDict.has_key(invdict[n]):
			if gv.loud:
				print "Removing %s and trying again"% invdict[n]
			del commandDict[invdict[n]]
			return get(commandDict, ip) # Call itself
		else:
			return {}
	else:
		for item in varBinds:
			
			n = oidFromDict(str(item[0]) , invdict)
			try:
				returndict[invdict[ n ] ] = str(item[1])
			except KeyError:
				print invdict
				print str(item[0]), str(item[1])
	return returndict
    
def getnext(commandDict, ip):
	from pysnmp.entity.rfc3413.oneliner import cmdgen
	commands = []
	invdict = {}
	returndict = {}
	for k,v in commandDict.items():
		v = v.replace('enterprises.','.1.3.6.1.4.1.')
		commands.append(v)
		invdict[v] = k
	for command in commands:
		errorIndication, errorStatus, errorIndex, varBindsTable = cmdgen.CommandGenerator().nextCmd(
		cmdgen.CommunityData('my-agent', 'public', 0), cmdgen.UdpTransportTarget((ip, 161)),
		command
		)
		results = []
		if errorStatus:
			for x in [ errorIndication, errorStatus, errorIndex, varBindsTable ]:
				print x
				print ""
		else:
			for item in varBindsTable:
				try:
					item = item[0][1]
				except:
					item = item[0]
				#print len(item)
				results.append(str(item))
		n = oidFromDict(command , invdict)
		returndict[invdict[n]] = results
	return returndict