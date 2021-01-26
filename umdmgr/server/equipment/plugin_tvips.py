#!/usr/bin/env python


from builtins import zip
from builtins import str
from builtins import range
from builtins import object
import helpers
from helpers import httpcaller, xmlhelper
from xml.dom import minidom

from .generic import HTTPError

class tvips(object):
	pass
	""" For shared class parts"""
	
class asiport(object):
	def __init__(self, d = None):
		if d:
				for k,v in list(d.items()):
					setattr(self, k,v)
	def getData(self):
		d = {}
		for k in ["id", "enable", "dir","dest","label"]:
			try:
				d[k] = getattr(self, k)
			except:
				continue
		return d
	
		
		
		

class TVG420(tvips):
	def __init__(self, ip, username, password):
		super(TVG420, self).__init__()
		self.ip = ip
		self.username = username
		self.password = password
		self.ports = []
		
		
		self.get_port_config()
		
	def get_port_config(self):
		#   Uncomment wehen ready to test from server
		try:
			response, stringfromserver = httpcaller.get(self.ip, '80', 'txp_get_tree?path=/ports&depth=4',  username= self.username, password=  self.password)
			if response['status'] != '200':
				raise HTTPError
				#	die( zip(response, "----------", "Bad response from server when getting information on ports from the TVIPS at ", self.ip))
			self.online = True
		except:
			self.online = False
		if self.online:
			xmldoc = xmlhelper.stringtoxml(stringfromserver)

			ids = xmlhelper.getAttributesFromTags('asi', '_id', xmldoc)
			enablelist = xmlhelper.getAttributesFromTags('asi', 'enable', xmldoc)
			labellist = xmlhelper.getAttributesFromTags('asi', 'label', xmldoc)
			dirlist  = xmlhelper.getAttributesFromTags('asi', 'dir', xmldoc) 
			destlist =  xmlhelper.getAttributesFromTags('dest', 'destip', xmldoc)
			ip_tx_rate =  xmlhelper.getAttributesFromTags('iptx', 'totrate', xmldoc)
			ip_rx_rate =  xmlhelper.getAttributesFromTags('iprx', 'totrate', xmldoc)
		else: #offline
			ids = list(range(8))
			enablelist = ["false"] *8
			labellist = [""] *8
			dirlist = [""] *8
			destlist = [""] *8
			ip_tx_rate = ["0"] *8
			ip_rx_rate = ["0"] *8
		self.ports = list(range(len(ids)))
		self.ids = []
		self.ip_tx_rate = []
		self.ip_rx_rate = []
		for id in ids:
			self.ids.append(int(id))
		
		for item in ip_tx_rate:
			self.ip_tx_rate.append(int(item))
		for item in ip_rx_rate:
			self.ip_rx_rate.append(int(item))
			
		self.enablelist = enablelist
		self.labellist = labellist
		self.dirlist = dirlist
		self.destlist = destlist
		if len(self.ports) != len(ids):
			self.ports = [asiport() for a in range(len(ids))]
		for item in range(len(self.ports)):
			self.ports[item].id = ids[item]
			self.ports[item].enable = enablelist[item]
			self.ports[item].dir = dirlist[item]
			self.ports[item].dest = destlist[item]
			self.ports[item].label = labellist[item]
	
	def get_tx_bw_only(self): #To be used after get_port_config
		
		for item in range(len(self.ids)):
			try:
				response, stringfromserver = httpcaller.get(self.ip, '80', 'txp_get?path=/ports/[' +str(self.ids[item])+ ']/iptx|_select:totrate',  username= self.username, password=  self.password)
				if response['status'] != '200':
					#die( zip(response, "----------", "Bad response from server when getting information on ports from the TVIPS at ", self.ip))
					raise "HTTP ERROR"
				self.online = True
			except:
				self.online = False
			if self.online:
			
				xmldoc = xmlhelper.stringtoxml(stringfromserver)
				ip_tx_rate =  xmlhelper.getAttributesFromTags('iptx', 'totrate', xmldoc)
				try:
					self.ip_tx_rate[item] = int(ip_tx_rate[0])
				except:
					self.ip_tx_rate[item] = 0
			else:
				self.ip_tx_rate[item] = 0
	def get_enable_only(self): #To be used after get_port_config
	
		try:
			response, stringfromserver = httpcaller.get(self.ip, '80', 'txp_get_tree?path=/ports&depth=1',  username= self.username, password=  self.password)
			if response['status'] != '200':
			#	die( zip(response, "----------", "Bad response from server when getting information on ports from the TVIPS at ", self.ip))
				raise Exception()
			
			xmldoc = xmlhelper.stringtoxml(stringfromserver)
			enablelist = xmlhelper.getAttributesFromTags('asi', 'enable', xmldoc)
			self.enablelist = enablelist
			self.online = True
		except:
			for item in range(len(self.enablelist)):
				self.enablelist[item] = "false"
			self.online = True
		
			
			
	def usage_by_label(self):
		return dict(list(zip(self.labellist, self.enablelist)))
		
	def usage_by_addr(self):
		return dict(list(zip(self.destlist, self.enablelist)))
	
	def bandwidth_by_label(self):
		return dict(list(zip(self.labellist, self.ip_tx_rate)))
		
	def bandwidth_by_addr(self):
		return dict(list(zip(self.destlist, self.ip_tx_rate)))
		
	
	def enable(self, port):
		"""enable asi port"""
		return self.enable_or_disable('true', port)
		
	def disable(self, port):
		"""disable asi port"""
		return self.enable_or_disable('false', port)
	
	def enable_or_disable(self, true_or_false, port):
		""" By name, multicast address or index
			This is both the enable and disable function and may only
			be called from within the class
			
		""" 
		if port in self.labellist:
			portnum = dict(list(zip(self.labellist, self.ids)))[port]
		elif port in self.destlist:
			portnum = dict(list(zip(self.destlist, self.ids)))[port]
		elif port in self.ids:
			portnum = port
		else:
			return "Port not found"
		
		# http://10.73.237.65/txp_set?path=/ports/[0]|enable:true
		response, stringfromserver = httpcaller.post(self.ip, '80', 'txp_set?path=/ports/['+ str(portnum )+']|enable:' + true_or_false, body="", username= self.username, password= self.password) 
		if response['status'] != '200':
			die( list(zip(response, "----------", "Bad response from server when getting streamstores from ", self.ip)))
			
		#print stringfromserver
		xmldoc = xmlhelper.stringtoxml(stringfromserver)
		
		
		
		
		status_text =  xmlhelper.getAttributesFromTags('status_detail', 'text', xmldoc)
			#there was an error
		if len(status_text) == 0:	
			status_text =  xmlhelper.getAttributesFromTags('status', 'status_text', xmldoc)
			#normal operation
		#return stringfromserver	
		try:
			status_text = status_text[0]
		except:
			status_text = "ERROR"
		return status_text
