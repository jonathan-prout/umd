#!/usr/bin/python

""" For extracting the DALLAS ID from a receiver
    Does not work witn RX8200
"""

from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class readWebTitle(HTMLParser):
        intitle = False
        titleText = ""
        def handle_starttag(self, tag, attrs):
                if tag == "title":
                        self.intitle=True
                else:
                        self.intitle=False
        def handle_endtag(self, tag):
                if tag == "title":
                        self.intitle=False
                
        def handle_data(self, data):
                if self.intitle:
                        self.titleText = data


def getEquipmentListCSV(filename):
        import csv
        fn = [ "ip", "model_id", "labelnamestatic"]
        #csv.register_dialect('dreams', quoting=csv.QUOTE_NONE, delimiter=',', lineterminator="\n",escapechar= "+" )
        #csvDialect = csv.get_dialect('dreams')
        try:	
                with open(filename, "rb") as fobj: #First read
                #ON WINDOWS BINARY MODE IS REQUIRED. This has no effect on NIX I think

                        fobj.seek(0)
        
                        rowlist= []
                        rowCounter = 0

                        for row in csv.DictReader(fobj, fieldnames = fn, dialect = "excel"):

                                rowCounter += 1
                                rowlist.append(row)
                
        except Exception as e:
            print "Program error: Could not open or read the file"
            print e
            rowlist = None
        return rowlist
            
def getEquipmentListSQL():
    import mysql, gv
    res = gv.sql.qselect("select ip, model_id, labelnamestatic from equipment")
    equipmentList = []
    for line in res:
        d = {}
        d["ip"], d["model_id"], d["labelnamestatic"] = line
        if d["model_id"] in ["RX1290", "TT1260", "Rx8200"]:
            equipmentList.append(d)
    return equipmentList

def getIDSNMP(machine):
    import snmp
    snmp_par = {"DallasID":".1.3.6.1.4.1.1773.1.3.200.3.7.1.8.2.0"}
    snmp_res = snmp.get(snmp_par, machine["ip"])
    if snmp_res.has_key("DallasID"):
        dal = snmp_res["DallasID"]
        dal = dal.strip()
        dal = dal.replace('"','')
        dal = dal.replace(" ", "")
    else:
        dal = ""
    return dal
def getIDWEB(machine):
    import httpcaller
    url ="http://%s/tcf?cgi=show&$path=/Customization"%machine["ip"]
    h, body = httpcaller.geturl(url)
    if h.has_key("status"):
        if h["status"] == "200":
            snline = ""
            for line in body.split("\n"):
                if "serial number" in line: # find the line with the SN
                    snline = line
                    for part in snline.split(","): #split it
                        part = part.replace("'","") # clean it
                        try:
                            i = int(part)
                        except ValueError:
                            i = 0
                        if i > 1000: # sn appears as large number
                            return str(i)
                        
                
    return ""
def getSN(machine):
    import snmp
    snmp_par = {"SN":".1.3.6.1.4.1.1773.1.1.3.1.8.0"}
    snmp_res = snmp.get(snmp_par, machine["ip"])
    if snmp_res.has_key("SN"):
        dal = snmp_res["SN"]
        dal = dal.strip()
        dal = dal.replace('"','')
        dal = dal.replace(" ", "")
    else:
        dal = ""
    return dal

def getWebTitle():
        import httpcaller
        url ="http://%s/"%machine["ip"]
        h, body = httpcaller.geturl(url)
        if h.has_key("status"):
            if h["status"] == "200":
               t = readWebTitle()
               t.feed(body)
               return t.titleText
        return ""

def writecsv(filename, equipmentList):
    import csv
    fn = ["ip","labelnamestatic", "sn", "model_id", "dallas"]
    with open(filename, "wb") as fobj:
        wr = csv.DictWriter(fobj, fieldnames = fn, dialect = "excel") #newline char mzst be LF		
        for row in equipmentList:
                wr.writerow(row)
def main(filename, equipmentList):

    import progressbar as pb
    
    for i in range(len(equipmentList)):
        pb.progressbar(i, len(equipmentList), headding="Progress", cls="True")
        equipmentList[i]["sn"] = getSN(equipmentList[i])
        if equipmentList[i]["model_id"] == "Rx8200":
            equipmentList[i]["dallas"] = getIDWEB(equipmentList[i])
        else:
            
            equipmentList[i]["dallas"] = getIDSNMP(equipmentList[i])
        
    writecsv(filename, equipmentList)
    
    print "file saved as %s"%filename
if __name__ == '__main__':
        import getopt, sys
        inputCSV = None
        outputCSV = None
        try:
                opts, args = getopt.getopt(sys.argv[1:], "o:,i:") 
        except getopt.GetoptError:   
                print "error in arguments get_dallas_id.py -o output filename -i if you want to specify an input CSV"
                                         
                sys.exit(2)
        for opt, arg in opts: 
                if opt in ("-o"):
                        outputCSV = arg
                if opt in ("-i"):
                        inputCSV = arg
        if inputCSV != None:
            equipmentList = getEquipmentListCSV(inputCSV)
        else:
            equipmentList = getEquipmentListSQL()
        if outputCSV == None:
            print "No filename for output file supplied"
        if all(( outputCSV, equipmentList)):
            main( outputCSV, equipmentList)
    
    

