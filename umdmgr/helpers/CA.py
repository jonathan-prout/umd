""" Ca Types

"""
import gv

CATypes = { "CLEAR":"CLEAR",
		   "Off":"CLEAR",
		   "On":"BISS",
		   "BISS":"BISS",
		   "CA":"CA"
}
def get():
	res = gv.sql.qselect("SELECT  `hex`, `value` FROM `encryption_types` WHERE 1")
	for line in res:
		try:
			hex, value = line
			CATypes[hex] = value
		except ValueError:
			continue
get()