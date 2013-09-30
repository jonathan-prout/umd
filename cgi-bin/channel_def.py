#!/usr/bin/python
numcolumns = 9


def opencsv(inputfile, format="file"):
	import csv
	if format == "buffer":
		#inputfile = inputfile.split("\n")
		csvfile = csv.reader(inputfile, delimiter=',', quotechar='|')
	else:
		csvfile = csv.reader(open(inputfile), delimiter=',', quotechar='|')
	okrows = []
	# Eliminate bad rows
	for row in csvfile:
		if len(row) == numcolumns: #Skip blank or bad rows
			if row[0] != 'satellite': # skip the row with the column names
				okrows.append(row)
	# don't need to close file
	return #okrows
	return inputfile

def createbackup():
	sql.qselect("TRUNCATE TABLE channel_def_backup")
	sql.qselect("INSERT INTO channel_def_backup SELECT * FROM channel_def")

def restorebackup():
	sql.qselect("TRUNCATE TABLE channel_def")
	sql.qselect("INSERT INTO channel_def SELECT * FROM channel_def_backup")


def upload(rows):
	import mysql, threading
	mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
	mysql.mysql.mutex = threading.RLock()
	sql = mysql.mysql()
	data = ["INSERT INTO `channel_def` (`sat`, `channel`, `frequency`, `pol`, `symbolrate`, `fec`, `rolloff`, `modulationtype`, `sd_hd`) VALUES"]
	for row in rows:
		# ('W3A', '1A18 22_SD', '10964.5', 'X', '13333.1', '7/8', '0.35', 'DVB-S', 'SD'),
		# W3A	1A18 22_SD	10964.5	X	13333.1	7/8	0.35	DVB-S	SD

		datarow ="('" + row[0] + "', '" + row[1] + "', '" + row[2] + "', '" + row[3] + "', '" + row[4] + "', '" + row[5] + "', '" + row[6] + "', '" + row[7] + "', '" + row[8] + "'),"
		data.append(datarow)
	data = " \n".join(data)
	data = data[:-1] #remove last ,
	#print data
	createbackup()
	sql.qselect("TRUNCATE TABLE channel_def")
	sql.qselect(data)
	
	
if __name__ == "__main__":
	rows = opencsv("rx_channels.csv")
	upload(rows)
	
	"""
	nothing = raw_input(str(len(rows)) + " rows found")
	counter = 0
	for row in rows:
		print ', '.join(row)
		if counter == 20:
			nothing = raw_input("more")
			counter = 0
		else:
			counter += 1
	"""
"""
mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
mysql.mysql.mutex = threading.RLock()
sql = mysql.mysql()
"""