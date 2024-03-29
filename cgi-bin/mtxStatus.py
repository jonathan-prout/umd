#!/opt/ebu/py37/bin/python 
import sys

try:
	import cgi, os
	import json
	import cgitb; cgitb.enable()
	import mysql, threading
except ImportError as e:
	print(str(e))
	sys.exit(1)
	
	



mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
mysql.mysql.mutex = threading.RLock()
mysql.mysql.dname="matrix"
sql = mysql.mysql()

dest_src = {}
src_dest = {}

for row in sql.qselect("SELECT `status`.`input`, `status`.`output` FROM `status` WHERE (`status`.`matrixid` =1);"):
	s = int(row[0])
	d = int(row[1])
	dest_src[d] = s
	if s not in src_dest:
		src_dest[s] = []	
	src_dest[s].append(d)
	

print("Content-Type: application/json")
print("")
print("dest_src = "+ json.dumps(dest_src))
print("src_dest = "+ json.dumps(src_dest))

	