import typing


class status_message(object):
	alarmMode = 1
	textMode = 0

	def __init__(self):
		self.topLabel = None
		self.bottomLabel = None
		self.cnAlarm = False
		self.recAlarm = False
		self.mv_input = -1
		self.strategy = "NoStrategy"
		self.colour = "#37e6ab"

	def __iter__(self) -> typing.Iterator:
		""" we pack this class into a list and call the list's iterator """
		""" Each item is a tuple of videoInput, level, line, mode"""
		level = ["TOP", "BOTTOM", "C/N", "REC"]
		line = [self.topLabel, self.bottomLabel, self.cnAlarm, self.recAlarm]
		mode = [self.textMode, self.textMode, self.alarmMode, self.alarmMode]
		msgList = []
		for i in range(4):
			if line[i]:
				msgList.append((self.mv_input, level[i], line[i], mode[i]))
		return msgList.__iter__()

	def setBottomLabel(self, s):
		self.bottomLabel = str(s)

	def setTopLabel(self, s):
		self.topLabel = str(s)