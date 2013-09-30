#!/usr/bin/env python
import cgi, os
import cgitb; cgitb.enable()
import mysql, threading
mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
mysql.mysql.mutex = threading.RLock()
sql = mysql.mysql()





def opencsv(inputfile, format="file"):
	numcolumns = 9
	import csv
	#print inputfile
	if format == "buffer":
		inputfile = inputfile.split('\n')
		csvfile = csv.reader(inputfile, delimiter=',', quotechar='|')
	else:
		csvfile = csv.reader(open(inputfile), delimiter=',', quotechar='|')
	okrows = []
	# Eliminate bad rows
	
	for row in csvfile:
		#print row
		if len(row) == numcolumns: #Skip blank or bad rows
			if row[0] != 'satellite': # skip the row with the column names
				#print row 
				#print "<br>"
				okrows.append(row)
	# don't need to close file
	return okrows
	# return inputfile

def createbackup():
	sql.qselect("TRUNCATE TABLE channel_def_backup")
	sql.qselect("INSERT INTO channel_def_backup SELECT * FROM channel_def")

def restorebackup():
	sql.qselect("TRUNCATE TABLE channel_def")
	sql.qselect("INSERT INTO channel_def SELECT * FROM channel_def_backup")


def upload(rows):

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
	print "Content-Type: text/html"
	print ""
	print "<html><body>"
	try: # Windows needs stdio set for binary mode.
		import msvcrt
		msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
		msvcrt.setmode (1, os.O_BINARY) # stdout = 1
	except ImportError:
		pass

	form = cgi.FieldStorage()

	# A nested FieldStorage instance holds the file
	try:
		fileitem = form['file']
		#fileitem = form.getfirst('file', 'empty')
	except: 
		message = "Fime not uploaded"
	# Test if the file was uploaded
	if fileitem.filename:
	#if fileitem != 'None':
		"""
		# strip leading path from file name to avoid directory traversal attacks
		fn = os.path.basename(fileitem.filename)
		open('files/' + fn, 'wb').write(fileitem.file.read())
		"""
		#message = fileitem.file.read()
		message = "Message"
		inputfile = fileitem.file.read()
		rows = opencsv(inputfile, format="buffer")
		
		if len(rows) < 32:
			message = "Error. Not enough rows."
		else:
			upload(rows)
			#rowsplit = "<br />".join(rows)
			message = 'The file was uploaded successfully. ' + str(len(rows)) + " rows uploaded"
		
		
		
	else:

		message = 'No file was uploaded'
		
	print """\
	<p>%s</p>
	<p><a href="http://10.73.196.231/umd/menu.php">BACK</a></p>
	</body></html>
	""" % (message)
