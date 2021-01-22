from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import str
from builtins import range
from builtins import object


class OmneonHelper(object):
	port = "80"
	def getrecorders(self, returnlist="namesonly"):
		# Returns a list of the configured recording channels (streamstores)
		streamnames = []
		streamaddresses = []
		streams = []
		from xml.dom import minidom
		import io
		from helpers import xmlhelper
		from helpers import httpcaller
		import os.path
		import json
		document = 'api/2/list/recorder/'
		response, stringfromserver = httpcaller.get(self.ip, self.port, document)
		msg =json.loads(stringfromserver)
		
		if msg["result"] == "OK":
			for ipgp in list(msg["data"].values()):
				for stream, value in list(ipgp.items()):
					if value != "STOPPED":
						streamnames.append(stream)
		streamnames = list(set(streamnames))
		
		"""
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
		"""
		if returnlist == "namesonly":
			return streamnames
		

		
		
	def getstreamstores(self, use="play", returnlist="dict"):
		# Returns a list of the configured recording channels (streamstores)
		streamnames = []
		streamaddresses = []
		streams = []
		from xml.dom import minidom
		import io
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
			return dict(list(zip(streamnames, streamaddresses)))		
			
			
	def getports(self):
		""" Returns 3 lists. Names of streams, ports used and multicast addresses """
			
		from helpers import xmlhelper
		from helpers import httpcaller
		#streams = streams_dict.keys()
		import json
		from . import iprange
		document = 'api/2/list/multicast'
		response, stringfromserver = httpcaller.get(self.ip, self.port, document)
		msg =json.loads(stringfromserver)
		
		
		
		
		counter = 1
		ports = []
		multicastaddresses = []
		owners = []
		if msg["result"] == "OK":
			for d in msg["data"]:
				if iprange.ismulticast(d["address"]):
					owners.append(d["name"])
					ports.append(d["port"])
					multicastaddresses.append(d["address"])
		return owners, ports, multicastaddresses	
