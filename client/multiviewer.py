"""

            UMD MANAGER v11
    Multiviewer Modeling Classes
    1.0 JP JUL 2012

"""
import telnetlib, Queue, signal, time


class boilerplate(object):
    """ Boilerplate stuff to inherit into sublcass that does stuff"""
    def shout(self, stuff):
        print "%s" % stuff
        
    def set_offline(self, callingFunc = None):
        self.offline = True
        self.shout("Problem when %s Now offline"% callingFunc)
        try:
            self.tel.close()
        except:
            pass
        
                    
    def get_offline(self):
            try:
                    return self.offline
            except:
                    return True
    def set_online(self):
        self.offline = False
    
    def errorHandler(self, signum, frame):
        print 'Error handler called with signal', signum
        
    def matchesPrevious(self, addr, level, line):
        """ Caches what the label is so it is not written next time """
        try:
            if self.previousLabel[addr][level] == line:
                
                return True
        except Exception as e:
            if isinstance(e, AttributeError):
                self.previousLabel = {}
            elif isinstance(e, KeyError):
                pass
            else:
                self.shout(str(e))
        if not self.previousLabel.has_key(addr):
            self.previousLabel[addr] = {}
        self.previousLabel[addr][level] = line
        return False
    
        
        
    def put(self, qitem):
        """videoInput, level, line, mode"""
        
        #self.q = Queue.Queue()
        if self.q.full():
            self.shout("%s at %s: UMD Queue full. Ignoring input"%(self.type, self.host))
            #raise Exception("Queue Full")
        else:
            if not self.get_offline():
                self.q.put(qitem)
    def close(self):
        try:
            self.tel.close()
        except:
            pass

class zprotocol(boilerplate):
    """ This class impliments Harris/Zandar Z protocol as a class
    TCP Port is implied, but expects an instance of a collections.queue object passed to perform FIFO queueing of UMD texts """
    
    
    def __init__(self, host):
        self.type = "Harris/Zandar"
        self.port = 4003
        self.host = host
        self.q = Queue.Queue(1000)
        self.connect()
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
            videoInput, level, line, mode = self.q.get()
            if not self.get_offline():
                if not self.matchesPrevious(videoInput, level, line):
                    self.writeline(videoInput, level, line)
        if self.last_cmd_sent < (time.time() -15 ):
            self.keepAlive()
        
            
        
    def __del__(self):
        try:
            self.tel.close()
        except:
            pass
        
class kaleido(boilerplate):

    def __init__(self, host):
        self.type = "Kaleido"
        self.port = 13000
        self.size = 16
        self.q = Queue.Queue(1000)
        self.host = host
        self.connect()
        self.make_default_input_table()

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
        except:
            self.set_offline("init")
            self.shout("Cannot connect to %s" %self.type)
        finally:
            #signal.alarm(0)          # Disable the alarm
            pass
    def make_default_input_table(self):
        self.lookuptable = {}
        for i in range(1, self.size+1):
            d = {
                "TOP": 0 + i,
                "BOTTOM": 100 + i,
                "C/N": 500 + i,
                "REC": 600 + i
            }
            self.lookuptable[i] = d
            
    def lookup(self, videoInput, level):
         return self.lookuptable[videoInput][level]
    
    def writeline(self, videoInput, level, line, mode):
        addr = self.lookup(videoInput, level)
        a = ""
        if mode == "ALARM":
            cmd = '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>\n' %(addr, line)
        else:
            
            cmd = '<setKDynamicText>set address="%s" text="%s" </setKDynamicText>\n' %(addr, line)
        """   
        # Set the signal handler and a 5-second alarm
        signal.signal(signal.SIGALRM, self.errorHandler)
        signal.alarm(5)
        """
        try:
            self.tel.write(cmd)
            a = self.tel.read_until("<ack/>", 1)
            if "<ack/>" not in a:
                shout(a)
        except:
            if "<nack/>" in a:
                shout("NACK ERROR in writeline when writing %s"% cmd)
            else:
                self.set_offline("writeline, %s, %s "%(line,a) )
        finally:
            #signal.alarm(0)          # Disable the alarm
            pass
        
    def refresh(self):
        while not self.q.empty():
            videoInput, level, line, mode = self.q.get()
            if not self.get_offline():
                if not self.matchesPrevious(videoInput, level, line):
                    self.writeline(videoInput, level, line, mode)
        
            
        
    def __del__(self):
        try:
            self.tel.close()
        except:
            pass