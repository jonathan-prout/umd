""" UMD Manager 11
	Harris Zandar multiviewers
	git note: moved from mukltiviewer.py
	"""
	
import telnetlib, Queue, signal, time
from generic import telnet_multiviewer

class zprotocol(telnet_multiviewer):
    """ This class impliments Harris/Zandar Z protocol as a class
    TCP Port is implied, but expects an instance of a collections.queue object passed to perform FIFO queueing of UMD texts """
    
    
    def __init__(self, host):
        self.mv_type = "Harris/Zandar"
        self.port = 4003
        self.host = host
        self.q = Queue.Queue(10000)
        self.connect()
        self.fullref = False
        self.last_cmd_sent = time.time()
        
    def connect(self):
        """
        # Set the signal handler and a 5-second alarm
        signal.signal(signal.SIGALRM, self.errorHandler)
        signal.alarm(5)
        
        """
        try:
            self.tel = telnetlib.Telnet(self.host, self.port)
            self.tel.write("\n")
            self.tel.read_until(">", 1)
            self.set_online()
            self.last_cmd_sent = time.time()
        except:
            self.set_offline("init")
        finally:
            #signal.alarm(0)          # Disable the alarm
            pass
            
    def keepAlive(self):
        try:
            self.tel.write("\n")
            self.tel.read_until(">", 1)
            self.last_cmd_sent = time.time()
        except:
            self.set_offline("keepalive")
            
    
    def writeline(self, videoInput, level, line):
        a = ""
        d = {"TOP":1, "BOTTOM":2}
        cmd = 'UMD_SET %s %s "%s"\n' %(videoInput, d[level], line)
        """
        # Set the signal handler and a 5-second alarm
        signal.signal(signal.SIGALRM, self.errorHandler)
        signal.alarm(5)
        
        """
        try:
            self.tel.write(cmd)
            a = self.tel.read_until(">", 1)
            self.last_cmd_sent = time.time()
        except:
            self.set_offline("writeline, %s, %s "%(line,a) )
        finally:
            #signal.alarm(0)          # Disable the alarm
            pass
    def refresh(self):
        
        while not self.q.empty():
            if self.fullref:
                break
            videoInput, level, line, mode = self.q.get()
            if not self.get_offline():
                if not self.matchesPrevious(videoInput, level, line):
                    self.writeline(videoInput, level, line)
        if self.fullref:
                self.qtruncate()
        if self.last_cmd_sent < (time.time() -15 ):
            self.keepAlive()
        
            
        
    def __del__(self):
        try:
            self.tel.close()
        except:
            pass