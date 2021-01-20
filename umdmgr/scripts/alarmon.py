#!/usr/bin/python


from __future__ import print_function
from builtins import range
import sys
def main(host, startaddress, endaddress, status):
	import umd
	cmd = []
	print("%s to %s" %(startaddress, endaddress))
	for x in range(startaddress, endaddress):
		cmd.append(    '<setKStatusMessage>set id="%s" status="%s"</setKStatusMessage>' %(x, status) )
	msg = "\n".join(cmd)
	#print msg
	umd.socketing(host, msg)


if __name__ == "__main__":
    try:
        host = sys.argv[1]
        startaddress = int(sys.argv[2])
        endaddress = int(sys.argv[3])
	status =  sys.argv[4]
	assert status in ["NORMAL", "MAJOR", "MINOR", "CRITICAL"]
    except:
        print("USAGE")
        print("alarmoff.py host startaddress endaddress")
        sys.exit(1)
    main(host, startaddress, endaddress, status)
    
