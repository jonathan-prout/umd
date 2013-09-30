#!/usr/bin/python

import telnetlib, threading
import sys
import getopt
import multiviewer
import time, datetime
### This is a simple test to send UMDs to the Harris Quad Split.
### Jonathan Prout, JUL 2012
import gv
gv.threadTerminationFlag = False
mythreads = []


def usage():
	print "I don't like your command line input."
	print 'do "clienttest.py -i <ip> -p <port> -1 "UMD text 1"' 
	sys.exit(1)

def getMultiviewer(mvType, host):
    
    if mvType in ["kaleido", "Kaleido"]:
        print "Starting Kaleido"
        return multiviewer.kaleido(host)
    else: #Harris/Zandar
        print "Starting Harris" 
        return multiviewer.zprotocol(host)

def main(argv, method='commandline', client=''):
	programStartTime = time.time()
        setumd1 = False
	setumd2 = False
	setumd3 = False
	setumd4 = False
	something_to_be_done = False
	host = "10.75.18.122"
	port = ""
        size = 4
	file = None
	"""
	if method == 'commandline':
		try:                                
			opts, args = getopt.getopt(argv, "di:s:f:m:") 
		except getopt.GetoptError:   
			print "error in arguments"
			usage()                          
			sys.exit(2) 
	else:
		opts = []
		args = []
		for arg in argv:
			try:
				optval, argval = arg.split("=")
				argval = argval.replace('"', '')
				argval = argval.replace("'", "")
				argval = argval.replace('_', ' ')
				
			except:
				optval = arg
				argval = ""
			opts.append([optval, argval])
			
	for opt, arg in opts:  
            #print opt +"," + arg              
            if opt in ("-i"):
                    host = arg
            elif opt == '-d':                
                    global _debug               
                    _debug = 1    
            elif opt in ("-p"):
                    port = arg
            elif opt in ("-s"):
                    size = int(arg)
            elif opt in ("-f"):
                    file = arg
            elif opt in ("-m"):
                    mvType = arg
                    
	"""
	mvType = "Kaleido"
        mv = getMultiviewer(mvType, host)
        """ BACKGROUND REFRESH THREAD """
        def startthreads():
            
            bg = myThread(1, "background refresh", 1, mv)
            bg.daemon = True
            mythreads.append(bg)
            bg.start()
        def restartThreads(mv):
            for x in xrange(len(mythreads)):
                threadID = mythreads[x].threadID
                name = mythreads[x].name
                counter = mythreads[x].counter
                instance = mythreads[x].instance
                bg = myThread(threadID, name, counter, mv)
                bg.daemon = True
                mythreads[x] = bg
                bg.start()
                print "%s restarted" %bg.name
        #startthreads()
        if file:
            with open(file, "r") as fobj:
                for i in range(size):
                    for level in ["TOP", "BOTTOM"]:
                        try:
                            line = fobj.readline()
                        except EOFError:
                            break
                        #videoInput, level, line, mode
                        mv.put( (i+1, level, line, "TEXT")   )
                mv.refresh()
                #time.sleep(1)
                
        
        else:
            print "Starting Counter Function. Press CTRL C to quit"
            counter = 0
            counter2 = 0
            
            while 1:
                #print "Iteration %s"% counter
                try:
                    
                    for i in range(size):
                        for level in ["TOP", "BOTTOM"]:
                            
                            line = "iter %s UMD %s, %s"%(counter, i+1, level)
                            mv.put( (i+1, level, line, "TEXT")   )
                    
                    mv.refresh()
                    time.sleep(1)
                    if mv.get_offline():
                        now = datetime.datetime.now()
                        print "Multiviewer has gone offline at %s"% now.strftime("%H:%M:%S")
                        print "Program ran for %s"% time.strftime("%H:%M:%S", time.gmtime(time.time() - programStartTime))
                        return
                    if counter2 == 300:
                        """RESTART MULTIVIEWER CONNECTION HERE """
                        gv.threadTerminationFlag = True
                        now = datetime.datetime.now()
                        t = time.time()
                        print "Attempting to join background thread at %s"% now.strftime("%H:%M:%S")
                        gv.threadTerminationFlag = True
                        for thread in mythreads:
                            thread.join(5)
                            if thread.isAlive(): #becomes is_alive() in later Python versions

                                print "Thread Timed out. :("
                        if time.gmtime(time.time() - t) > 0:
                            print "That took %s"% time.strftime("%H:%M:%S", time.gmtime(time.time() - t))
                        type = mv.type
                        host = mv.host
                        mv.close()
			return #quit
                        mv = getMultiviewer(mvType, host)
                        
                        gv.threadTerminationFlag = False
                        restartThreads(mv)
                        counter2 = 0
                except KeyboardInterrupt:
                    return
                counter += 1
                counter2 += 1
                
class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, instance):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.instance = instance
    def run(self):
        #print "Starting " + self.name
        refresh(self.instance)
        #print "Exiting " + self.name
def refresh(mv):            
    while not gv.threadTerminationFlag:
        if mv.get_offline():
            print "Attempting to reconnect"
            mv.connect()
            if mv.get_offline(): #still
                time.sleep(5) # wait between connection attempts
        else:
            mv.refresh()
	    time.sleep(1)
    #print "Leaving thread as termintation flag set"
        
if __name__ == '__main__':
    #main(sys.argv[1:])
    main(None)