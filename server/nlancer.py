#!/usr/bin/python

import os, re, string,threading,time,datetime
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys

SLEEPTIME=5
#shellcommand=r'/root/programming/umd/mymain.py'
#shellcommand=r'/root/programming/mymain.py'
shellcommand=r'/var/www/programming/server/mymain.py'


def thread(sleeptime):
	import time, random
	time.sleep(sleeptime)

if __name__ == "__main__":
	while 1:
		t1=threading.Thread(target=thread(SLEEPTIME))
		t1.setDaemon(1)
		t1.start()
		t1.join()
		os.system(shellcommand)
