#!/usr/bin/python
import sys
def main(host, startaddress, endaddress):
    import umd
    cmd = []
    for x in range(startaddress, endaddress):
    cmd.append(    '<setKStatusMessage>set id="%s" status="DISABLE"</setKStatusMessage>' %x )
    umd.socketing(host, "\n".join(cmd))


if __name__ == "__main__":
    try:
        host = sys.argv[1]
        startaddress = sys.argv[2]
        endaddress = sys.argv[2]
    except:
        print "USAGE"
        print "alarmoff.py host startaddress endaddress"
        sys.exit(1)
    main(host, startaddress, endaddress)
    