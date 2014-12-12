import gv

defaultCast = [(int, 0),
			(float, 0.0),
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

		

class irdResult(object):
	commands = ["e.id","s.servicename","s.aspectratio","s.ebno","s.pol",
		    "s.castatus","e.kaleidoaddr","e.InMTXName","e.OutMTXName",
		    "s.channel","s.framerate","e.labelnamestatic", 	"e.name",
		    "s.modulationtype","s.modtype2","s.asi","s.videoresolution",
		    "e.model_id","s.muxbitrate","s.videostate", "s.status", "s.muxstate", "e.kid",
		    "s.OmneonRec", "s.TvipsRec", "e.doesNotUseGateway", "e.Demod"]
	
	
	def __init__(self, equipmentID, res = None):
		self.equipmentID = int(equipmentID)
		if res:
			self.res = res
		else:
			refresh()
		self.cmap = {}
		for x in range(len(self.commands)):
			self.cmap[self.commands[x]] = x
	
	def refresh(self):
		request = "SELECT " + ",".join(self.commands) + " FROM equipment e, status s WHERE e.id = s.id AND e.id = '%d'"%self.equipmentID
		self.res = gv.sql.qselect(request)
	
	def getKey(self,k):
		try:
			return self.res[self.cmap[k]]
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
			
			
	def getInput(self):
		pass
		
	def getLock(self ):
		pass
	def getCN(self):
		pass
	def getChannel(self):
		pass
	def getServiceName(self):
		pass
	def getInput(self):
		pass
	def getMatrixInput(self):
		if self.getInput() in  ['IP', "ASI"]:
				if self.getInput() == "ASI":
					if self.getKey("e.InMTXName") != "NULL":
						for matrix in gv.asiMatrixes:
							src = sourceNameFromDestName(self.getKey("e.InMTXName"))
							if src: break
						else:
							src = ""
		return src
						
	def getVideoFormat(self):
		pass
	def getDemod(self):
		demod = cast(int, self.getKey("e.Demod"))
		if demod != 0:
				if not gv.equip.has_key(demod):
					gv.equip[demod] = irdResult(demod)
				
				if gv.equip[demod].getOnline():
					return demod
		else:
			
			
		return 0
					

	def getOnline(self):
		return getKey("s.status") == "Online"

	