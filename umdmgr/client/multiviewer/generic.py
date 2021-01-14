"""
    UMD Manager 12
    generic multiviewer base class
    git note: moved from multiviewer.py
    """
from __future__ import print_function
import telnetlib, Queue, signal, time
import typing


class status_message(object):
    def __init__(self):
        self.topLabel = None
        self.bottomLabel = None
        self.cnAlarm = False
        self.recAlarm = False
        self.mv_input = -1
        self.strategy = "NoStrategy"
        self.alarmMode = 1
        self.textMode = 0

    def __iter__(self) -> typing.Iterator:
        """ we pack this class into a list and call the list's iterator """
        """ Each item is a tuple of videoInput, level, line, mode"""
        level = ["TOP",         "BOTTOM",           "C/N",              "REC"]
        line = [self.topLabel,  self.bottomLabel,   self.cnAlarm,       self.recAlarm]
        mode = [self.textMode,  self.textMode,      self.alarmMode,     self.alarmMode ]
        msgList = []
        for i in range(4):
            if line[i]:
                msgList.append( (self.mv_input, level[i], line[i], mode[i] ))
        return msgList.__iter__()
    
    def setBottomLabel(self, s):
        self.bottomLabel = str(s)
    def setTopLabel(self, s):
        self.topLabel = str(s)
        
        
class multiviewer(object):
    """ Base class multiviewers MUST inherit """
    lookuptable = {}
    def shout(self, stuff):
        print("%s" % stuff)   

    def qtruncate(self):
        self.fullref = False
        self.q = Queue.Queue(1000)
        self.previousLabel = {}

    def get_offline(self):
            try:
                    return self.offline
            except:
                    return True
    def set_online(self):
        self.offline = False
    
    def errorHandler(self, signum, frame):
        print(('Error handler called with signal', signum))
        
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
        if addr not in self.previousLabel:
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


class telnet_multiviewer(multiviewer):
    """ Boilerplate stuff to inherit into sublcass that does stuff"""

        
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
                        

    def close(self):
        try:
            self.tel.close()
        except Exception as e:
            pass


class testmultiviewer(multiviewer):
    lookuptable = {}
    def __init__(self, host):
        self.mv_type = "test"
        
        self.size = 96
        self.q = Queue.Queue(10000)
        self.host = host
        
        self.fullref = False
        self.make_default_input_table()
        
    def make_default_input_table(self):
        self.lookuptable = {}
        for i in range(1, self.size+1):
            d = {
                "TOP": "0" + str(i),
                "BOTTOM": 100 + i,
                "C/N": 500 + i,
                "REC": 600 + i
            }
            self.lookuptable[i] = d
    def refresh(self):
        vi = {}
        for v in self.lookuptable.values():
            v["new"] = "False"
        print("refresh")
        while not self.q.empty():
            if self.fullref:
                break
            sm = self.q.get()
            if sm:
                print(self.host + ": %s (%s) status %s//%s"%(sm.mv_input, sm.strategy, sm.topLabel, sm.bottomLabel))
                for alarm in [sm.cnAlarm, sm.recAlarm]:
                    alarm = {True:"MAJOR", False:"DISABLE"}[alarm]
                    
                for videoInput, level, line, mode in sm:
                    if not line: line = ""
                    if not self.get_offline():
                        if videoInput not in vi:
                            vi[videoInput] = {}
                        vi[videoInput][level] = line
                    vi[videoInput]["strategy"] = sm.strategy
                    vi[videoInput]["new"] = "True"
        print(vi)
        for k,v in vi.iteritems():
            self.lookuptable[k] = v
        if self.fullref:
                    self.qtruncate()
        fbuffer = ['<HTML><HEAD><link rel="stylesheet" type="text/css" href="multiviewer.css"></HEAD><BODY><table border="0"width="100%"><tr>']
        i = 0
        line = ""
        for key in self.lookuptable.keys():
            if i == 4: i = 0
            if i == 0:
                line += "<tr>"
            line += "<td> input %s<br>"%key
            for k,v in self.lookuptable[key].iteritems():
                line += '<p class="%s">%s:%s</p>'%(k,k,v)
                
            line +="</td>"
            i += 1	
            if i == 4:
                line += "</tr>"
                fbuffer.append(line)
                line = ""
        fbuffer.append(line)
        fbuffer.append("""</tr>
                    </table>
                    </body>
                    </html>""")
        with open("/var/www/umd/umdtest%s.html"%self.host, "w") as fobj:
            fobj.write("\n".join(fbuffer))
        
    def get_offline(self):
        return False
