class OmneonHelper(object):

	def getrecorders(self, returnlist="dict"):
		# Returns a list of the configured recording channels (streamstores)
		streamnames = []
		streamaddresses = []
		streams = []
		from xml.dom import minidom
		import StringIO
		from helpers import xmlhelper
		from helpers import httpcaller
		import os.path

		document = 'ipgp.nodes.rec.xml'
		response, stringfromserver = httpcaller.get(self.ip, '9980', document)
		xmldoc = xmlhelper.stringtoxml(stringfromserver)
		#xmldoc = minidom.parse(document)
		#document.close()
		
		ipgridportiplist = xmlhelper.getAttributesFromTagsConditional('ipgridport', 'ip', xmldoc, 'InUse', 'True')
		#streams = ipgridportiplist
		#debug(ipgridportiplist)
		for item in range(len(ipgridportiplist)):
			#response, stringfromserver = httpcaller.get(item, '9998', 'streamstores')
			waiting_for_http = True
			while waiting_for_http:
				try:
					response, stringfromserver = httpcaller.get(str(ipgridportiplist[item]), '9998', 'recorders/started') #The last is a caching value of 5 seconds. New streamstores will not be seen for that long unless the cache is flushed
				except:
					response = {"status":"500"}
					stringfromserver = ""
				if response['status'] != '200':
					#self.offline = True
					#die( zip(response, "----------", "Bad response from server when getting streamstores from ", ipgridportiplist[item]))
					continue
				else:
					waiting_for_http = False
			try:
				xmlfromserver = xmlhelper.stringtoxml(stringfromserver)
			except:
				continue
			#print xmlfromserver.toxml()
			
			#newstreams = xmlhelper.getAttributesFromTagsConditional('StreamStoreInfo', 'StreamId', xmlfromserver, 'InUse', 'true')
			newstreams = xmlhelper.getAttributesFromTagsConditional('RecorderInfo', 'StreamId', xmlfromserver, 'Status', 'RECORDING')
			newstreams += xmlhelper.getAttributesFromTagsConditional('RecorderInfo', 'StreamId', xmlfromserver, 'Status', 'LISTENING')
			#print newstreams
			if returnlist == "byip":
				streams.append(newstreams) #newstreams is a multidimensional list. Each list of newstreams is itself a list item.
			else:
				for x in newstreams:
					if x not in streamnames:
						streamnames.append(x)
						streamaddresses.append(ipgridportiplist[item])
		if returnlist == "namesonly":
			return streamnames
		elif returnlist == "byip":
			return ipgridportiplist, streams
		else:
			return dict(zip(streamnames, streamaddresses))

			
	def getstreamstores(self, use="play", returnlist="dict"):
		# Returns a list of the configured recording channels (streamstores)
		streamnames = []
		streamaddresses = []
		streams = []
		from xml.dom import minidom
		import StringIO
		from helpers import xmlhelper
		from helpers import httpcaller
		import os.path
		if use == "rec":

			document = 'ipgp.nodes.rec.xml'
		elif use == "export":

			document = 'ipgp.nodes.export.xml'
		else:
			document = 'ipgp.nodes.play.xml'
		response, stringfromserver = httpcaller.get(self.ip, '9980', document)
		xmldoc = xmlhelper.stringtoxml(stringfromserver)
		#document.close()
		
		ipgridportiplist = xmlhelper.getAttributesFromTagsConditional('ipgridport', 'ip', xmldoc, 'InUse', 'True')
		#streams = ipgridportiplist
		#debug(ipgridportiplist)
		for item in range(len(ipgridportiplist)):
			#response, stringfromserver = httpcaller.get(item, '9998', 'streamstores')
			try:
				response, stringfromserver = httpcaller.getcache(str(ipgridportiplist[item]), '9998', 'streamstores', '30') #The last is a caching value of 15 minutes. New streamstores will not be seen for that long unless the cache is flushed
			except:
				response = {"status":"500"}
				stringfromserver = "" 
			if response['status'] != '200':
				#self.offline = True
				#return {}
				continue
				#die( zip(response, "----------", "Bad response from server when getting streamstores from ", ipgridportiplist[item]))
				
			
			xmlfromserver = xmlhelper.stringtoxml(stringfromserver)
			#print xmlfromserver.toxml()
			
			#newstreams = xmlhelper.getAttributesFromTagsConditional('StreamStoreInfo', 'StreamId', xmlfromserver, 'InUse', 'true')
			newstreams = xmlhelper.getAttributesFromTags('StreamStoreInfo', 'StreamId', xmlfromserver)
			#print newstreams
			if returnlist == "byip":
				streams.append(newstreams) #newstreams is a multidimensional list. Each list of newstreams is itself a list item.
			else:
				for x in newstreams:
					if x not in streamnames:
						streamnames.append(x)
						streamaddresses.append(ipgridportiplist[item])
		if returnlist == "namesonly":
			return streamnames
		elif returnlist == "byip":
			return ipgridportiplist, streams
		else:
			return dict(zip(streamnames, streamaddresses))		
			
			
	def getports(self):
		""" Returns 3 lists. Names of streams, ports used and multicast addresses """
		streams_dict = self.getstreamstores(use="rec")
		#players_dict = getstreamsinks(use="playersonly")
		# http://10.72.0.4:9998/streamsources/W3-B3A
		# http://10.72.0.9:9998/streamsinks/GW-2
		# because I want to neatly index everything..
		
		from helpers import xmlhelper
		from helpers import httpcaller
		streams = streams_dict.keys()
		#players = 	players_dict.keys()
		totallength = len(streams)
		counter = 1
		ports = []
		multicastaddresses = []
		owners = []
		for stream in streams:
			#progressbar(counter, totallength, headding="Retreiving Ports and Multicast Addresses")
			url = "streamsources/" + stream
			response, stringfromserver = httpcaller.get(streams_dict[stream], '9998', url)
			
			if response['status'] != '200': 
				#die( zip(response, "----------", "Bad response from server when getting streamstores from ", ipgridportiplist[item]))
				self.offline = True
				return [ [], [], []  ]
				
			xmlfromserver = xmlhelper.stringtoxml(stringfromserver)
			port = xmlhelper.getAttributesFromTags('SourceAddress', 'IpPort', xmlfromserver)	
			multicastaddress = xmlhelper.getAttributesFromTags('SourceAddress', 'IpAddress', xmlfromserver)	
			ports.append(port[0])
			multicastaddresses.append(multicastaddress[0])
			owners.append(stream)
			counter += 1
		"""
		for player in players:
			#progressbar(counter, totallength, headding="Retreiving ports and Multicast addresses")
			url = "streamsinks/" + player
			response, stringfromserver = httpcaller.get(players_dict[player], '9998', url)
			
			if response['status'] != '200': 
				die( zip(response, "----------", "Bad response from server when getting streamstores from ", ipgridportiplist[item]))
			xmlfromserver = xmlhelper.stringtoxml(stringfromserver)
			port = xmlhelper.getAttributesFromTags('SinkAddress', 'IpPort', xmlfromserver)	
			multicastaddress = xmlhelper.getAttributesFromTags('SinkAddress', 'IpAddress', xmlfromserver)	
			ports.append(port[0])
			multicastaddresses.append(multicastaddress[0])
			owners.append(player)
			counter += 1
		"""
		return owners, ports, multicastaddresses	