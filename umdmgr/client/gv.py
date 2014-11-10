# UMD MANAGER CLIENT


threadTerminationFlag = False
programTerminationFlag = False
display_server_status = "Unknown"
loud = True
from helpers import mysql
import threading
#mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
#mysql.mysql.mutex = threading.RLock()
sql = mysql.mysql()

sql.semaphore = threading.BoundedSemaphore(value=1)
sql.mutex = threading.RLock()

labelcache = {}
