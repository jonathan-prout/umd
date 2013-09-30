#!/usr/bin/python
import os, re, string,threading,time,datetime
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys

SLEEPTIME=5
shellcommand=r'/var/www/programming/client/umd.py'
shellcommand2=r'/var/www/programming/client/customlabel.py'


def thread(sleeptime):
	import time, random
	time.sleep(sleeptime)

if __name__ == "__main__":
	#print "***********   please do not close this window      ****************"
	while 1:
		t1=threading.Thread(target=thread(SLEEPTIME))
		t1.setDaemon(1)
		t1.start()
		t1.join()
		os.system(shellcommand)
		os.system(shellcommand2)
