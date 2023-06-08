#!/opt/ebu/py37/bin/python
import cgi, os
import queue as Queue
import cgitb

cgitb.enable()
import multiviewer

multiviewer.openMv = None
import mysql, threading

mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
mysql.mysql.mutex = threading.RLock()
sql = mysql.mysql()


class kal(multiviewer.KX):
    clearAlarmsOnConnect = False
    msgQ = Queue.Queue()

    def shout(self, s):
        self.msgQ.put(s)


def printheaders():
    print("Content-Type: text/html")
    print("")
    print("")
    print("""<html><head><script>
                <!--
                function land(ref, target)
                {
                lowtarget=target.toLowerCase();
                if (lowtarget=="_self") {window.location=loc;}
                else {if (lowtarget=="_top") {top.location=loc;}
                else {if (lowtarget=="_blank") {window.open(loc);}
                else {if (lowtarget=="_parent") {parent.location=loc;}
                else {parent.frames[target].location=loc;};
                }}}
                }
                function jump(menu)
                {
                ref=menu.choice.options[menu.choice.selectedIndex].value;
                splitc=ref.lastIndexOf("*");
                target="";
                if (splitc!=-1)
                {loc=ref.substring(0,splitc);
                target=ref.substring(splitc+1,1000);}
                else {loc=ref; target="_self";};
                if (ref != "") {land(loc,target);}
                }
                //-->
                </script><title>UMD Manager Kaleido Actions</title></head><body>""")
    print('<form action="dummy" method="post"><select name="choice" size="1" onChange="jump(this.form)">')
    print('<option value="#">Please Select</option>')


def close():
    print('</body></html>')
    if multiviewer.openMv is not None:
        multiviewer.openMv.close()


def getmsgs():
    if multiviewer.openMv != None:
        if not multiviewer.openMv.msgQ.empty():
            print("<br>\nThe multiviewer has the following messages\n<br>\n")
        while not multiviewer.openMv.msgQ.empty():
            print(multiviewer.openMv.msgQ.get())
            print("<br>\n")


def nice_name(s_input):
    s = s_input.replace("ip", "input ")
    s = s.replace("_", " ")
    s = s.replace("fs", "fullscreen")
    return s


def main():
    printheaders()
    fs = cgi.FieldStorage()

    mvList = sql.qselect("SELECT * FROM `Multiviewer` WHERE 1")
    MVNAME = 1
    MVIP = 2
    mvDict = {}
    for mv in mvList:
        print('<option value="kalaction.py?mv=%s">%s</option>' % (mv[MVNAME], mv[MVNAME]))
        mvDict[mv[MVNAME]] = mv[MVIP]
    print("</select></form></td>")

    selectedMV = fs.getfirst("mv")
    if selectedMV in mvDict.keys():

        multiviewer.openMv = kal(mvDict[selectedMV])

    else:
        print("Select Kaleido to open<br>")

        close()
        return

    if multiviewer.openMv.get_offline():
        print("Could not connect to Multiviewer<br>")
        getmsgs()
        close()
        return
    if os.environ['REQUEST_METHOD'] == 'POST':
        action = fs.getfirst("action")
        if action != None:
            multiviewer.openMv.setAction(action)
            if multiviewer.openMv.get_offline():
                print("Command rejected by Multiviewer<br>")
                getmsgs()
                close()
                return
            else:
                print("Command '%s' submitted OK<br>\n" % nice_name(action))

    actions = multiviewer.openMv.getActionList()
    print("")
    if actions != []:
        print("The following commands are available on this Kaleido")
        for action in actions:
            print('<form method="post" action="#">')
            print('<input type="hidden" name="action" value="%s"><br>' % action)
            print('<input type="submit" value="%s">' % nice_name(action))
            print('</form>')
    else:
        print("No commands are available on this Kaleido")

    close()


if __name__ == "__main__":
    main()
