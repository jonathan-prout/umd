"""
    UMD Manager 12
    generic multiviewer base class
    git note: moved from multiviewer.py
    """
import telnetlib, Queue, signal, time


class telnet_multiviewer(object):
    """ Boilerplate stuff to inherit into sublcass that does stuff"""
    lookuptable = {}
    def shout(self, stuff):
        print "%s" % stuff
        
    def set_offline(self, callingFunc = None):
        self.offline = True
        self.shout("Problem with %s when %s Now offline"% (self.host, callingFunc))
        try:
            self.tel.close()
        except:
            pass
        
    def writeStatus(self, status, queued=True):
            """ Write Errors to the multiviewer """
            
            klist = sorted(self.lookuptable.keys())
            for key in range(0, len(klist), 16):
                    if queued:
                        try: 
                                self.put( (klist[key], "BOTTOM", status, "TEXT") )
                        except:
                                pass        
                    else:
                        try:
                            self.writeline(klist[key], "BOTTOM", status, "TEXT")
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
            pass
            #self.shout("%s at %s: UMD Queue full. Ignoring input"%(self.mv_type, self.host))
            #raise Exception("Queue Full")
        else:
            if not self.get_offline():
                self.q.put(qitem)
    def close(self):
        try:
            self.tel.close()
        except:
            pass
    def qtruncate(self):
        self.fullref = False
        self.q = Queue.Queue(1000)
        self.previousLabel = {}