"""
	UMD Manager 12
	generic multiviewer base class
	git note: moved from multiviewer.py
	"""
from __future__ import print_function
from future import standard_library

import client.multiviewer.status

standard_library.install_aliases()
from builtins import zip
from builtins import str
from builtins import range
import queue
from abc import abstractmethod, ABCMeta, ABC
from client import gv, labelmodel


def get_mv_input_from_database(mvHost, mvInput):
	""" Return the muliviewer input from the database """
	fields = ["strategy", "equipment", "inputmtxid", "inputmtxname", "customlabel1", "customlabel2"]
	fn = []
	cmap = {}
	i = 0
	for f in fields:
		fn.append("`mv_input`.`%s`" % f)
		cmap[f] = i
		i += 1

	cmd = "SELECT "
	cmd += " , ".join(fn)
	cmd += "FROM `mv_input`"
	cmd += "WHERE ((`mv_input`.`multiviewer` =%d) AND (`mv_input`.`input` =%d))" % (gv.mvID[mvHost], mvInput)

	return dict(list(zip(fields, gv.sql.qselect(cmd)[0])))


class multiviewer(ABC):
	""" Base class multiviewers MUST inherit """
	__metaclass__ = ABCMeta

	def __init__(self):
		self.previousLabel = {}
		self.lookuptable = {}
		self.qtruncate()

	def shout(self, stuff):
		print("%s" % stuff)

	def qtruncate(self):
		self.fullref = False
		self.q = queue.Queue(1000)
		self.previousLabel = {}

	def get_offline(self):
		try:
			return self.offline
		except:
			return True

	def set_online(self):
		self.offline = False

	def errorHandler(self, signum, frame):
		print(('Error handler called with signal', signum))

	def matchesPrevious(self, addr, level, line):
		""" Caches what the label is so it is not written next time """
		try:
			if self.previousLabel[addr][level] == line:
				return True
		except Exception as e:
			if isinstance(e, AttributeError):
				self.previousLabel = {}
			elif isinstance(e, KeyError):
				pass
			else:
				self.shout(str(e))
		if addr not in self.previousLabel:
			self.previousLabel[addr] = {}
		self.previousLabel[addr][level] = line
		return False

	def put(self, qitem):
		"""videoInput, level, line, mode"""

		if self.q.full():
			pass
		# self.shout("%s at %s: UMD Queue full. Ignoring input"%(self.mv_type, self.host))
		# raise Exception("Queue Full")
		else:
			if not self.get_offline():
				self.q.put(qitem)

	def getStatusMesage(self, mvInput, mvHost=None):
		mvHost = mvHost or self.host
		with gv.equipDBLock:

			happyStatuses = ["RUNNING"]
			pollstatus = gv.getPollStatus().upper()
			displayStatus = gv.display_server_status.upper()

			sm = client.multiviewer.status.status_message()

			res = get_mv_input_from_database(mvHost, mvInput)
			# print cmd
			# print res
			if all((pollstatus in happyStatuses, displayStatus in happyStatuses)):
				try:
					if gv.equip[int(res["equipment"])] is not None:
						tlOK = True
					else:
						tlOK = False
					e = None
				except KeyError as e:
					tlOK = False
				if all((int(res["strategy"]) == int(inputStrategies.equip), tlOK)):
					sm = gv.equip[res["equipment"]].getStatusMessage()
					assert sm is not None
					sm.strategy = "equip"
				elif res["strategy"] == inputStrategies.matrix:
					mtxIn = gv.mtxLookup(res["inputmtxname"])
					if gv.getEquipByName(mtxIn):
						sm = gv.equip[gv.getEquipByName(mtxIn)].getStatusMessage()
						sm.strategy = "matrix + equip"
						assert sm is not None
					else:
						sm = labelmodel.matrixResult(mtxIn).getStatusMessage()
						assert sm is not None
						sm.strategy = "matrix no equip"
				elif res["strategy"] == inputStrategies.indirect:
					sm = labelmodel.matrixResult(res["inputmtxname"]).getStatusMessage()
					assert sm is not None
					sm.strategy = "indirect"
				elif res["strategy"] == inputStrategies.label:
					if res["customlabel1"]:
						sm.topLabel = res["customlabel1"]
					if res["customlabel2"]:
						sm.bottomLabel = res["customlabel2"]
					sm.strategy = "label"
			else:
				try:
					if gv.equip[int(res["equipment"])] is not None:
						tlOK = True
					else:
						tlOK = False
					e = None
				except KeyError as e:
					tlOK = False
				if all((int(res["strategy"]) == int(inputStrategies.equip), tlOK)):
					sm.topLabel = gv.equip[int(res["equipment"])].isCalled()
					sm.bottomLabel = " "
					sm.strategy = "equip"
				elif res["strategy"] == inputStrategies.label:
					if res["customlabel1"]:
						sm.topLabel = res["customlabel1"]
					if res["customlabel2"]:
						sm.bottomLabel = res["customlabel2"]
					sm.strategy = "label"
				else:
					sm.topLabel = res["inputmtxname"]
					# sm.bottomLabel = "%s, %s %s,%s"%(res["equipment"],len(gv.equip.keys()),e, int(res["strategy"]) )
					sm.bottomLabel = " "
					sm.strategy = "matrix"
				if mvInput % 16 == 1:
					sm.bottomLabel = "Display: %s, Polling:%s" % (displayStatus, pollstatus)

			sm.mv_input = mvInput

		return sm

	@abstractmethod
	def writeline(self, videoInput, level, line, mode, buffered=True):
		pass

	def writeStatus(self, status, queued=True):
		""" Write Errors to the multiviewer """

		klist = sorted(self.lookuptable.keys())
		for key in range(0, len(klist), 16):
			if queued:
				try:
					self.put((klist[key], "BOTTOM", status, "TEXT"))
				except:
					pass
			else:
				try:
					self.writeline(klist[key], "BOTTOM", status, "TEXT", buffered=False)
				except:
					pass


class TelnetMultiviewer(multiviewer, metaclass=ABCMeta):
	""" Boilerplate stuff to inherit into sublcass that does stuff"""
	__metaclass__ = ABCMeta

	def set_offline(self, callingFunc=None):
		self.offline = True
		self.shout("Problem with %s when %s Now offline" % (self.host, callingFunc))
		try:
			self.tel.close()
		except:
			pass

	def close(self):
		try:
			self.tel.close()
		except Exception as e:
			pass


class TestMultiviewer(multiviewer):

	def __init__(self, host):
		super(TestMultiviewer, self).__init__()
		self.mv_type = "test"
		self.lookuptable = {}
		self.size = 96
		self.q = queue.Queue(10000)
		self.host = host
		self.fullref = False
		self.make_default_input_table()

	def make_default_input_table(self):
		self.lookuptable = {}
		for i in range(1, self.size + 1):
			d = {
				"TOP": "0" + str(i),
				"BOTTOM": 100 + i,
				"C/N": 500 + i,
				"REC": 600 + i
			}
			self.lookuptable[i] = d

	def refresh(self):
		vi = {}
		for v in list(self.lookuptable.values()):
			v["new"] = "False"
		print("refresh")
		while not self.q.empty():
			if self.fullref:
				break
			sm = self.q.get()
			if sm:
				print(self.host + ": %s (%s) status %s//%s" % (sm.mv_input, sm.strategy, sm.topLabel, sm.bottomLabel))
				for alarm in [sm.cnAlarm, sm.recAlarm]:
					alarm = {True: "MAJOR", False: "DISABLE"}[alarm]

				for videoInput, level, line, mode in sm:
					if not line: line = ""
					if not self.get_offline():
						if videoInput not in vi:
							vi[videoInput] = {}
						vi[videoInput][level] = line
					vi[videoInput]["strategy"] = sm.strategy
					vi[videoInput]["new"] = "True"
		print(vi)
		for k, v in vi.items():
			self.lookuptable[k] = v
		if self.fullref:
			self.qtruncate()
		fbuffer = [
			'<HTML><HEAD><link rel="stylesheet" type="text/css" href="multiviewer.css"></HEAD><BODY><table border="0"width="100%"><tr>']
		i = 0
		line = ""
		for key in list(self.lookuptable.keys()):
			if i == 4: i = 0
			if i == 0:
				line += "<tr>"
			line += "<td> input %s<br>" % key
			for k, v in self.lookuptable[key].items():
				line += '<p class="%s">%s:%s</p>' % (k, k, v)

			line += "</td>"
			i += 1
			if i == 4:
				line += "</tr>"
				fbuffer.append(line)
				line = ""
		fbuffer.append(line)
		fbuffer.append("""</tr>
					</table>
					</body>
					</html>""")
		with open("/var/www/umd/umdtest%s.html" % self.host, "w") as fobj:
			fobj.write("\n".join(fbuffer))

	def get_offline(self):
		return False
