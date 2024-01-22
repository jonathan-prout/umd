"""

            UMD MANAGER v11
    Multiviewer Modeling Classes
    1.0 JP JUL 2012

"""
import telnetlib, signal, time
import queue as Queue


class Telnet(telnetlib.Telnet):
    def write(self, s, *args, **kwargs):
        return super(Telnet, self).write(s.encode("UTF-8"), *args, **kwargs)

    def read_until(self, s, *args, **kwargs):
        return super(Telnet, self).read_until(s.encode("UTF-8"), *args, **kwargs).decode("UTF-8")


class boilerplate(object):
    """ Boilerplate stuff to inherit into sublcass that does stuff"""

    def shout(self, stuff):
        print("%s" % stuff)

    def set_offline(self, callingFunc=None):
        self.offline = True
        self.shout("Problem with %s when %s Now offline" % (self.host, callingFunc))
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
        print('Error handler called with signal', signum)

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

        # self.q = Queue.Queue()
        if self.q.full():
            pass
            # self.shout("%s at %s: UMD Queue full. Ignoring input"%(self.mv_type, self.host))
            # raise Exception("Queue Full")
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


class zprotocol(boilerplate):
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
            self.tel = Telnet(self.host, self.port)
            self.tel.write("\n")
            self.tel.read_until(">", 1)
            self.set_online()
            self.last_cmd_sent = time.time()
        except:
            self.set_offline("init")
        finally:
            # signal.alarm(0)          # Disable the alarm
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
        d = {"TOP": 1, "BOTTOM": 2}
        cmd = 'UMD_SET %s %s "%s"\n' % (videoInput, d[level], line)
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
            self.set_offline("writeline, %s, %s " % (line, a))
        finally:
            # signal.alarm(0)          # Disable the alarm
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
        if self.last_cmd_sent < (time.time() - 15):
            self.keepAlive()

    def __del__(self):
        try:
            self.tel.close()
        except:
            pass


class kaleido(boilerplate):
    mv_type = "Kaleido"
    port = 13000
    size = 96
    timeout = 10

    def __init__(self, host):
        self.mv_type = "Kaleido"
        self.port = 13000
        self.size = 96
        self.q = Queue.Queue(10000)
        self.host = host
        self.connect()
        self.fullref = False
        self.make_default_input_table()

    def connect(self):

        """
        # Set the signal handler and a 5-second alarm
        signal.signal(signal.SIGALRM, self.errorHandler)
        signal.alarm(5)
        """
        try:
            import gv
            assert (gv.programTerminationFlag == False)
            self.tel = Telnet(self.host, self.port)
            self.tel.write("\n")
            self.tel.read_until(">", self.timeout)
            self.set_online()

        except Exception as e:
            self.set_offline("init")
            self.shout("Cannot connect to %s" % self.host)
            self.shout(e)
        finally:
            # signal.alarm(0)          # Disable the alarm
            pass

    def make_default_input_table(self):
        self.lookuptable = {}
        for i in range(1, self.size + 1):
            d = {
                "TOP": "0" + str(i),
                "BOTTOM": 100 + i,
                "C/N": 500 + i,
                "REC": 600 + i,
                "COMBINED": 200 + i
            }
            self.lookuptable[i] = d

    def lookup(self, videoInput, level):
        return self.lookuptable[int(videoInput)][level]

    def writeline(self, videoInput, level, line, mode):
        try:
            addr = self.lookup(videoInput, level)
        except:
            return
        a = ""
        if mode == "ALARM":
            if self.AlarmCapable:
                cmd = '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>\n' % (addr, line)
            else:
                return
        else:
            if self.lowAddressBug:
                if addr < 100:
                    addr = "0" + str(addr)
            cmd = '<setKDynamicText>set address="%s" text="%s" </setKDynamicText>\n' % (addr, line)
        """
        # Set the signal handler and a 5-second alarm
        signal.signal(signal.SIGALRM, self.errorHandler)
        signal.alarm(5)
        """
        try:
            self.tel.write(cmd)
            a = self.tel.read_until("<ack/>", self.timeout)
            if "<ack/>" not in a:
                self.shout(a)
        except:
            if "<nack/>" in a:
                self.shout("NACK ERROR in writeline when writing %s" % cmd)
            else:
                self.set_offline("writeline, %s, %s " % (line, a))
        finally:
            # signal.alarm(0)          # Disable the alarm
            pass

    def setAction(self, actionName):

        cmd = '<setKFireAction>set name="%s"</setKFireAction>\n' % actionName
        try:
            self.tel.write(cmd)
            a = self.tel.read_until("<ack/>", self.timeout)
            if "<ack/>" not in a:
                self.shout(a)
        except:
            if "<nack/>" in a:
                self.shout("Multiviewer did not recognise the action named %s" % actionName)
            else:
                self.set_offline("writeline, %s, %s " % (line, a))
        finally:
            # signal.alarm(0)          # Disable the alarm
            pass

    def getActionList(self):
        import xml.etree.ElementTree as E
        a = ""
        cmd = '<getKActionList/>\n'
        try:
            self.tel.write(cmd)
            a = self.tel.read_until("</kActionList>", self.timeout)
            if "</kActionList>" not in a:
                self.shout(a)
                return []
        except:
            if "<nack/>" in a:
                return []
        xmlData = E.fromstring(a)
        returnList = []
        for el in xmlData.findall("action"):
            returnList.append(el.text)
        return returnList

    def refresh(self):
        while not self.q.empty():
            if self.fullref:
                break
            videoInput, level, line, mode = self.q.get()
            if not self.get_offline():
                if not self.matchesPrevious(videoInput, level, line):
                    self.writeline(videoInput, level, line, mode)
        if self.fullref:
            self.qtruncate()

    def __del__(self):
        try:
            self.tel.close()
        except:
            pass

    def clearalarms(self):
        """ KX has alarms on on startup, so clear them """
        for alarm_type in ["REC", "C/N"]:
            for mv_input in self.lookuptable.keys():
                self.put((mv_input, alarm_type, "DISABLE", "ALARM"))


class KX(kaleido):
    mv_type = "KX"
    port = 13000
    size = 96
    AlarmCapable = True
    lowAddressBug = False
    fullref = False
    clearAlarmsOnConnect = True

    def __init__(self, host):
        self.q = Queue.Queue(1000)
        self.host = host

        self.make_default_input_table()
        self.connect()

    def connect(self):
        super(KX, self).connect()
        if self.clearAlarmsOnConnect:
            self.clearalarms()


class K2(kaleido):
    mv_type = "K2"
    AlarmCapable = False
    lowAddressBug = False
    port = 13000
    size = 32
    fullref = False

    def __init__(self, host):
        self.q = Queue.Queue(100)
        self.host = host

        self.fullref = False
        self.make_default_input_table()
        self.connect()


class KX16(KX):
    mv_type = "KX-16"
    size = 16


class KXQUAD(KX):
    mv_type = "KX-QUAD"
    size = 4


openMv = None
