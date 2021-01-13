#!/usr/bin/python


from __future__ import print_function
import sys
def main(host, startaddress, endaddress):
	import umd
	cmd = []
	print("%s to %s" %(startaddress, endaddress))
	for x in range(startaddress, endaddress):
		cmd.append(    '<setKStatusMessage>set id="%s" status="DISABLE"</setKStatusMessage>' %x )
	msg = "\n".join(cmd)
	#print msg
	umd.socketing(host, msg)


if __name__ == "__main__":
    try:
        host = sys.argv[1]
        startaddress = int(sys.argv[2])
        endaddress = int(sys.argv[3])
    except:
        print("USAGE")
        print("alarmoff.py host startaddress endaddress")
        sys.exit(1)
    main(host, startaddress, endaddress)
    