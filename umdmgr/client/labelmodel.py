import gv
from multiviewer.generic import status_message

defaultCast = [(int, 0),
			(float, 0.0),
			(bool, False),
			(str, "")
			
		]

def cast(func, obj):
	""" Safe type casting function, returns a default value if not available. Pass func or known objType """
	try:
		return func(obj)
	except ValueError:
		for f, v in defaultCast:
			if func == f:
				return v


def bitrateToStreamcode(muxbitrate):
	tolerance = float(0.125)
	#streamcodes == []:
	if not gv.streamcodes:
		gv.streamcodes = gv.sql.qselect("SELECT `name`, `bitrate` FROM `streamcodes` WHERE 1")
	
	
	try:
		bitratefloat = float(muxbitrate)
		bitratefloat = (bitratefloat / 1000000) #bps to mbps
	except:
		bitratefloat = 0
	
	
	for name, streamBitrate in gv.streamcodes:
		streamBitratee = float(streamBitrate)
		if(streamBitrate - tolerance  < bitratefloat <streamBitrate + tolerance):
			bitratestring = name
			break
		else:
			bitratestring = str(bitratefloat)[:4]
	return bitratestring		

class matrixResult(object):
	def __init__(self, name, level = "SDI"):
		self.name = name
		self.level = level
	def refresh(self):
		pass
	def getTopLabel(self):
		src = gv.mtxLookup(self.name, self.level)
		if src:
			toplabel = "%s > %s"%(src, self.name)
		else:
			toplabel = "%s"%self.name
	
	def getBottomLabel(self):
		return " "		
	def getStatusMessage(self):
		sm = status_message()

		sm.cnAlarm = False
		sm.recAlarm = False
		sm.topLabel = self.getTopLabel()
		sm.boottomLabel = self.getBottomLabel()
		return sm
	

class irdResult(object):
	
	remove_hz = True
	
	commands = ["e.id","s.servicename","s.aspectratio","s.ebno","s.pol",
		    "s.castatus","e.InMTXName","e.OutMTXName",
		    "s.channel","s.framerate","e.labelnamestatic", 	"e.name",
		    "s.modulationtype","s.modtype2","s.asi","s.videoresolution",
		    "e.model_id","s.muxbitrate","s.videostate", "s.status", "s.muxstate", 
		    "s.OmneonRec", "s.TvipsRec", "e.doesNotUseGateway", "e.Demod"]
	
	
	def __init__(self, equipmentID, res = None):
		self.equipmentID = int(equipmentID)
		if res:
			if isinstance(res, dict):
				self.res = res
			elif isinstance(res[0], dict):
                                self.res = res[0]
			elif isinstance(res, tuple):
				 self.res = dict(zip(self.commands,res))

		else:
			self.refresh()
		self.cmap = {}
		for x in range(len(self.commands)):
			self.cmap[self.commands[x]] = x
	
	def refresh(self):
		request = "SELECT " + ",".join(self.commands) + " FROM equipment e, status s WHERE e.id = s.id AND e.id = '%d'"%self.equipmentID
		try:
			self.res = dict(zip(self.commands,gv.sql.qselect(request)[0]))
		except:
			self.res = {}
	def getKey(self,k):
		try:
			return self.res[k]
		except KeyError:
			return ""
	def getKeyFromDemod(self, k):
		demod = self.getDemod()
		if demod:
			
			if self.getInput() in  ['IP', "ASI"]: #UNIT is using an external demod. Use that demod's settings
				return gv.equip[demod].getKey(k)
		return self.getKey(k)	
	
	def isCalled(self, name = ""):
		""" Compare name, matrix or label name with a given name or give the label name """
		if name:
			for k in ["e.OutMTXName", "e.labelnamestatic", "e.name"]:
				if name == self.getKey(k):
					return True
			return False
		else:
			return self.getKey("e.labelnamestatic")
			
	def getVideoResolution(self):
		res = self.getKey("s.videoresolution")
		try:
			res = int(res)
		except:
			res = 0
		if res == 480:
			res = 525
		if res == 576:
			res = 625
		return res
		
	def getInput(self):
		return self.getKey("s.asi")
		
	def getLock(self ):
		lockstate = True
		if any((self.res["e.Demod"] != 0 , self.res["s.asi"] == "SAT")):
			if (self.res["s.ebno"] == ".-1dB"):
				lockstate = False
			elif ('-' in self.res["s.ebno"]):
				lockstate = False
			elif (self.res["s.ebno"] == "100.10dB"):
				lockstate = False
			elif (self.res["s.ebno"] == "0.0dB"):
				lockstate = False
		if (len(self.getServiceName()) != 0): #clearly if there is a service name it is self.res["s.muxstate"]
			lockstate = True
		if (self.res["s.videostate"] == "Running"):
			lockstate = True
		if (self.res["s.muxstate"] == "Unlock"):
			lockstate = False
		return lockstate

	def getCN(self):
		
		ebno = self.getKeyFromDemod("s.ebno").replace("dB","").strip()
		ebno = ebno.replace('"','')
		ebno = ebno.replace(' ','')
		ebno = ebno.replace('+','')
		return cast( float, ebno)
		
	
	def getChannel(self):
		return self.getKey("s.channel")
	def getServiceName(self):
		return self.getKey("s.servicename")

	def getMatrixInput(self):
		if self.getInput() in  ['IP', "ASI"]:
				if self.getInput() == "ASI":
					if self.getKey("e.InMTXName") != "NULL":
						
						src = gv.mtxLookup(self.getKey("e.InMTXName"),self.getInput())
							
						return src
						
	
	def getDemod(self):
		demod = cast(int, self.getKey("e.Demod"))
		if demod != 0:
				if not gv.equip.has_key(demod):
					gv.equip[demod] = irdResult(demod)
				
				if gv.equip[demod].getOnline():
					return demod
		else:
			src = gv.getEquipByName(self.getMatrixInput())
			if gv.equip.has_key(src):
				if gv.equip[src].getInput() == "SAT":
					return src
				
			
		return 0
					
	def getModScheme(self):
		dvbmode = self.getKey("s.modulationtype")
		dvbmode = dvbmode.replace("DVB-", "")
		return dvbmode
	
	def getOnline(self):
		return self.getKey("s.status") == "Online"
	
	def getBitrate(self):
		return self.getKey("s.muxbitrate")
	
	def getFramerate(self):
		framerate = self.getKey("s.framerate").replace(" ","")
		if self.remove_hz:
			framerate = framerate.replace("Hz","")
		return cast(float ,framerate)
	def getca(self):
		return self.getKey("s.castatus")
	def getTopLabel(self):
		if self.getOnline():
			
			bitratestring = str( bitrateToStreamcode(self.getBitrate()) )
				
									
			if (len(self.getChannel()) != 0): #Have we found the channel?
				if self.getLock(): # Channel found and service running
					if any((self.getInput() == "SAT", self.getDemod())): #NOT ASI
						rname = self.isCalled().split(" ")[0].replace("RX","")
						toplabeltext = rname + " " + self.getChannel()[0:max(0,(len(self.getChannel())-3))]
						toplabeltext += " " + bitratestring
						toplabeltext += "" + self.getModScheme() + "| " + self.getServiceName()
					else:
						toplabeltext = self.isCalled() + " " + bitratestring + ""  + "| " + self.getServiceName()
				else: #no input
					toplabeltext = self.isCalled() + " " + self.getChannel() + "" + self.getModScheme()

			else: # Channel missing and service running
				if self.getLock():
					toplabeltext = self.isCalled() + " " + bitratestring + ""  + "| " + self.getServiceName()
				else:
					toplabeltext = self.isCalled()
		else:
			toplabeltext = self.isCalled()
		return toplabeltext.replace("\n","")
	
	def getBottomLabel(self):
			if self.getOnline():
				if self.getLock():
					bottomumd = ""
					vres = self.getVideoResolution()
					HD = vres >= 720
					if (HD == True):
						bottomumd +=  "%d/%f"%(vres,self.getFramerate())
					else:
						if self.getKey("s.aspectratio") != "":
							SD = str(vres)
							if SD != "":
								bottomumd +=   SD[0] + "_"+self.getKey("s.aspectratio")
							else:
								bottomumd += self.getKey("s.aspectratio")
						else:
							bottomumd +=   str(vres)
					if self.getDemod():
						src = self.getKeyFromDemod("e.labelnamestatic")
					else:
						src = self.getMatrixInput()
					if src:
						bottomumd += " %s:%s "%(self.getInput()[0], src)
					else:
						if self.getInput() != "SAT":
							bottomumd += " %s "%self.getInput()
					if self.getInput() == "SAT":
						bottomumd += " %0.1fdB "%self.getCN()
					
					bottomumd +=  "/" +  " " + self.getca() 
					
					
					
					#sendumd += "<setKDynamicText>set address=\""+rx["e.rx["e.labeladdr"]2"]+"\" text=\""+res[i][5]+" "+res[i][1]
					"""sendumd = sendumd + " " + res[i][2] + " " + res[i][3]+" Biss:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n" """
					#sendumd = sendumd + " / " + res[i][2] + " " +" BS:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n"
											# sendumd = sendumd + " / " + res[i][2] + " " +" BS:"+res[i][4]+" "+res[i][10]+"\"</setKDynamicText>\n"
					
					
				else: #IF No lock, we write "NO LOCK" at the bottom
					if self.getDemod():
						src = self.getKeyFromDemod("e.labelnamestatic")
					else:
						src = self.getMatrixInput()
					if not src: src = ""
					bottomumd = "%s:%s NO LOCK"%(self.getInput(), src)
			else:	
				bottomumd="OFFLINE"
			return bottomumd.replace("\n","")
		
	def getStatusMessage(self):
		sm = status_message()
		d = {True:"MAJOR", False:"DISABLE"}
		cnOK = all((self.getCN()	< 2, self.getCN()	> 0 ))
		sm.cnAlarm = not cnOK
		sm.recAlarm = any( (all( (cast(bool, self.getKey("s.OmneonRec")), cast(bool, self.getKey("s.TvipsRec"))) ),
					all(( cast(bool, self.getKey("s.OmneonRec")), cast(bool, self.getKey("e.doesNotUseGateway")) ))
					) )
		
		sm.topLabel = self.getTopLabel()
		sm.boottomLabel = self.getBottomLabel()
	
		return sm