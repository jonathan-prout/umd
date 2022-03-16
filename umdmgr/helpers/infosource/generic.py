""" Interface description for the infosource classes
"""


from builtins import object
class IInfoSourceMixIn(object):
	""" Infosource Mixin interface """
	#prefsDict = {} needed but must be created at runtime
	def levelNames(self):
		""" return dict of available item numbers and their names
		"""
		pass
	def destNames(self, level):
		""" return dict of available destination numbers and their names
		"""
		pass
	def sourceNames(self, level):
		""" return dict of available source numbers and their names
		"""
		pass
	def sources(self, level):
		""" return a List of the sources for a given level
		"""
		pass
	def destinations(self, level):
		""" return a List of the destination for a given level
		"""
		pass
	def size(self, level):
		""" Return a tuple of two integers, destinations, sources for given level
		"""
	def levels(self):
		""" return list of available level numbers
		"""
	
