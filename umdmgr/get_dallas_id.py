#!/usr/bin/python

""" For extracting the DALLAS ID from a receiver
    
"""

from HTMLParser import HTMLParser
from helpers import httpcaller

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
    from helpers import mysql
    sql = mysql.mysql()
    res = sql.qselect("select ip, model_id, labelnamestatic from equipment")
    equipmentList = []
    for line in res:
        d = {}
        d["ip"], d["model_id"], d["labelnamestatic"] = line
        if d["model_id"] in ["RX1290", "TT1260", "Rx8200", "Rx8200-2RF", "Rx8200-4RF"]:
            d["model_id"] = d["model_id"].replace("-2RF","").replace("-4RF","")
            equipmentList.append(d)
    return equipmentList

class ird(object):
        snurl = "tcf?cgi=show&%24record=@Slot%5E0&%24path0=/Device%20Info/Modules&%24path=/Device%20Info/Modules"
        dalurl = ["tcf?cgi=show&$path=/Conditional%20Access"]
        dalstr = ["m_caDir5UniqueId"]
        sn = 0
        canSNMP = True
        def __init__(self, machine):
                self.machine = machine
        
        def getSN(self):
                if not self.sn:
                     dal = self.getSN_SNMP()
                     if dal == "":
                        self.canSNMP = False
                        try:
                                dal = self.getSN_WEB()
                        except:
                                dal = ""
                        if dal == "": dal = 0
                self.sn = dal
                return self.sn
        
        def getID(self):
                if self.canSNMP:
                        return self.getIDSNMP()
                else:
                        for i in range(len(self.dalurl)):
                                try:
                                        n = self.getIDWEB(i)
                                        if n >1000:
                                                return n
                                except:
                                        continue
                        return 0
                                
        def getIDSNMP(self):
            from helpers import snmp
            snmp_par = {"DallasID":".1.3.6.1.4.1.1773.1.3.200.3.7.1.8.2.0"}
            snmp_res = snmp.get(snmp_par, self.machine["ip"])
            if snmp_res.has_key("DallasID"):
                dal = snmp_res["DallasID"]
                dal = dal.strip()
                dal = dal.replace('"','')
                dal = dal.replace(" ", "")
            else:
                dal = ""
            return dal
        
        def getIDWEB(self, i=0):
                
                url ="http://%s/"%self.machine["ip"] +self.dalurl[i]
                try:
                        h, body = httpcaller.geturl(url)
                except:
                        h, body = [{},""]
                if h.has_key("status"):
                    if h["status"] == "200":
                        snline = ""
                        for line in body.split("\n"):
                            if self.dalstr[i] in line: # find the line with the SN
                                snline = line
                                for part in snline.split(","): #split it
                                    part = part.replace("'","") # clean it
                                    part = part.replace(" ","")
                                    try:
                                        i = int(part)
                                    except ValueError:
                                        i = 0
                                    if i > 1000: # sn appears as large number
                                        return str(i)
                                
                                
                        
                return ""
        def getSN_SNMP(self):
            from helpers import snmp
            snmp_par = {"SN":".1.3.6.1.4.1.1773.1.1.3.1.8.0"}
            snmp_res = snmp.get(snmp_par, self.machine["ip"])
            if snmp_res.has_key("SN"):
                dal = snmp_res["SN"]
                dal = dal.strip()
                dal = dal.replace('"','')
                dal = dal.replace(" ", "")
            else:
                dal = ""
            return dal
        def getSN_WEB(self):
            import httpcaller
            url ="http://%s/"%self.machine["ip"] + sel.snurl
            try:
                h, body = httpcaller.geturl(url)
            except:
                        h, body = [{},""]
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
        def getWebTitle(self):
                import httpcaller
                url ="http://%s/"%self.machine["ip"]
                try:
                        h, body = httpcaller.geturl(url)
                except:
                        h, body = [{},""]
                if h.has_key("status"):
                    if h["status"] == "200":
                       t = readWebTitle()
                       t.feed(body)
                       return t.titleText
                return ""
class rx8200(ird):
        dalurl = ["tcf?cgi=show&$path=/Customization" ,"tcf?cgi=show&$path=/Customization"]
        snurl = "tcf?cgi=show&%24record=@Slot%5E0&%24path0=/Device%20Info/Modules&%24path=/Device%20Info/Modules"
        dalstr = ["serial number", "Serial Number"]
        canSNMP = False
        
def getIRD(machine):
        if "Rx8200" in machine["model_id"]:
                return rx8200(machine)
        else:
                return ird(machine)
        
        
def writecsv(filename, equipmentList):
    import csv
    fn = ["ip","labelnamestatic", "sn", "model_id", "dallas"]
    with open(filename, "wb") as fobj:
        wr = csv.DictWriter(fobj, fieldnames = fn, dialect = "excel", delimiter = ";") #newline char mzst be LF	  delimiter=";"	
        for row in equipmentList:
                wr.writerow(row)
def main(filename, equipmentList):

    from helpers import progressbar as pb
    
    for i in range(len(equipmentList)):
        pb.progressbar(i, len(equipmentList), headding="Progress", cls="True")
        curIrd = getIRD(equipmentList[i])
        equipmentList[i]["sn"] = curIrd.getSN()
        if equipmentList[i]["labelnamestatic"] == "auto":
                equipmentList[i]["labelnamestatic"] = curIrd.getWebTitle()
        
        equipmentList[i]["dallas"] = curIrd.getID()

        
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
                print "opt %s arg %s"%(opt,arg)
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
    
    

