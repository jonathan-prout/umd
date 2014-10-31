import gv
import plugin_tvips
from plugin_omneon import OmneonHelper

def enum(iterable):
	
	d = {}
	for i in range(len(iterable)):
		d[i] = iterable[i]
	return d


class oidWorkaround(equipment):
	def __init__(self, modelType):
		self.modelType = modelType
		self.getoid()
