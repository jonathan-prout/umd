#!/usr/bin/python
import os, re, sys

class encoderatom:
	def __init__(self,id,status,servicename,muxbitrate,muxscrambling,muxbissword,muxencrypedword,videoprofilelevel,
	muxstatus,videobitrate,videopid,videoaspectratio,videogoplen,videogopstruc,videobandwidth,videomaxbitrate,
	videodelay,temperature):
		self.id = id
		self.status = status
		self.servicename = servicename
		self.muxbitrate = muxbitrate
		self.muxscrambling = muxscrambling
		self.muxbissword = muxbissword
		self.muxencrypedword = muxencrypedword
		self.videoprofilelevel = videoprofilelevel
		self.muxstatus = muxstatus
		self.videobitrate = videobitrate
		self.videopid = videopid
		self.videoaspectratio = videoaspectratio
		self.videogoplen = videogoplen
		self.videogopstruc = videogopstruc
		self.videobandwidth = videobandwidth
		self.videomaxbitrate = videomaxbitrate
		self.videodelay = videodelay
		self.temperature = temperature

		
	def getId(self):
		return self.id
	
	def getStatus(self):
		return self.status
			
	def getServiceName(self):
		return self.servicename
		
	def getMuxBitRate(self):
		return self.muxbitrate
		
	def getMuxScrambling(self):
		return self.muxscrambling
	
	def getMuxBissWord(self):
		return self.muxbissword
		
	def getMuxEncrypedWord(self):
		return self.muxencrypedword
		
	def getVideoProfileLevel(self):
		return self.videoprofilelevel
	
	def getMuxStatus(self):
		return self.muxstatus
	
	def getVideoBitRate(self):
		return self.videobitrate
		
	def getVideoPid(self):
		return self.videopid
		
	def getVideoAspectRatio(self):
		return self.videoaspectratio
	
	def getVideoGOPLen(self):
		return self.videogoplen
	
	def getVideoGOPStruc(self):
		return self.videogopstruc
		
	def getVideoBandwidth(self):
		return self.videobandwidth
	
	def getVideoMaxBitrate(self):
		return self.videomaxbitrate
	
	def getVideoDelay(self):
		return self.videodelay
	
	def getTemperature(self):
		return self.temperature	
			
	def setId(self,id):
		self.id = id
	
	def setStatus(self,status):
		self.status = status
		
	def setServiceName(self,servicename):
		if (len(servicename) >=10):
			servicename = servicename[0:9]		
		self.servicename = servicename
		
	def setMuxBitRate(self,muxbitrate):
		self.muxbitrate = muxbitrate
	
	def setMuxScrambling(self,muxscrambling):
		self.muxscrambling = muxscrambling
	
	def setMuxBissWord(self,muxbissword):
		self.muxbissword = muxbissword
		
	def setMuxEncryptedWord(self,muxencryptedword):
		self.muxencryptedword = muxencryptedword
	
	def setVideoProfileLevel(self,videoprofilelevel):
		if (videoprofilelevel == "0"):
			self.videoprofilelevel = "4:2:0"
		if (videoprofilelevel == "1"):
			self.videoprofilelevel = "4:2:2"
		if (videoprofilelevel == "2"):
			self.videoprofilelevel = "4:2:2"
		if (videoprofilelevel == "3"):
			self.videoprofilelevel = "4:2:2"
		#self.videoprofilelevel = videoprofilelevel
		
	def setMuxStatus(self,muxstatus):
		self.muxstatus = muxstatus
	
	def setVideoBitRate(self,videobitrate):
		self.videobitrate = videobitrate
	
	def setVideoPid(self,videopid):
		self.videopid = videopid
			
	def setVideoAspectRatio(self,videoaspectratio):
		if (videoaspectratio == "2"):
			self.videoaspectratio = "16:9"
		if (videoaspectratio == "3"):
			self.videoaspectratio = "4:3"
		if (videoaspectratio == ""):
			self.videoaspectratio = ""
	
	def setVideoGOPLen(self,videogoplen):
		self.videogoplen = videogoplen
	
	def setVideoGOPStruc(self,videogopstruc):
		self.videogopstruc = videogopstruc
	
	def setVideoBandwidth(self,videobandwidth):
		self.videobandwidth = videobandwidth
		
	def setVideoMaxBitrate(self,videomaxbitrate):
		self.videomaxbitrate = videomaxbitrate
		
	def setVideoDelay(self,videodelay):
		self.videodelay = videodelay
	
	def setTemperature(self,temperature):
		self.temperature = temperature



