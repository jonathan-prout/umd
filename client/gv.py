# UMD MANAGER CLIENT


threadTerminationFlag = False
programTerminationFlag = False
display_server_status = "Unknown"
loud = True
import mysql
import threading
mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
mysql.mysql.mutex = threading.RLock()
sql = mysql.mysql()
labelcache = {}