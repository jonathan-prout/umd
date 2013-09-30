#!/usr/bin/env python

import cgi, os
import cgitb; cgitb.enable()
import mysql, threading
mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
mysql.mysql.mutex = threading.RLock()
sql = mysql.mysql()

print "Content-Type: text/html"
print ""
print "<html><body>"
try:
	sql.qselect("TRUNCATE TABLE channel_def")
	sql.qselect("INSERT INTO channel_def SELECT * FROM channel_def_backup")
	message = "Channel Presets restored from backup successfully."
except:
	message = "Error restoring Channel Presets from file.."

print """\
<p>%s</p>
<p><a href="http://10.73.196.231/umd/menu.php">BACK</a></p>
</body></html>
""" % (message)
