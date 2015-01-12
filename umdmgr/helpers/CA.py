""" Ca Types

"""


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
			hex_str, value = line
			CATypes[hex_str] = value
		except ValueError:
			continue
#get()