#!/usr/bin/python
import os, re, string,threading
import sys,time,datetime
import mysql
 
def service():
 
        mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
        mysql.mysql.mutex = threading.RLock()
        sql = mysql.mysql()
 
        status = ""
        dreams = ""
       # frequency        symbolrate        fec        rolloff        modulationtype
       
        status_request = "SELECT e.satellite,s.pol,s.frequency,s.symbolrate,s.rolloff,s.modulationtype,e.labelnamestatic FROM equipment e, status s WHERE e.id = s.id"
      #  dreams_request = "SELECT c.sat,c.pol,c.frequency,c.symbolrate,c.rolloff,c.modulationtype,c.channel FROM channel_def c"
        try:
                status = sql.qselect(status_request)
       #         dreams = sql.qselect(dreams_request)
        except MySQLdb.Error, e:
                print "SQL Connection Error at ",now.strftime("%H:%M:%S")
                print "Error %d: %s" % (e.args[0], e.args[1])
        #sql.close()
 
        for i in range(0,len(status)):
          result = ""
          #print status[i][0]
          channel_request = "SELECT c.channel, c.modulationtype FROM channel_def c WHERE ((c.sat =\"" + str(status[i][0]) + "\") AND (c.pol =\"" + str(status[i][1]) + "\") AND (c.frequency LIKE \"" + str(status[i][2]) + "%\") AND (c.symbolrate  LIKE \"" + str(status[i][3]) + "%\"))"
          #print channel_request
          result = sql.qselect(channel_request)
          if(len(result) != 0 ):
             channel = str(result[0][0]) 
             modulation = str(result[0][1])
             channel = channel[0:(len(channel)-3)]
             #channel = str(status[i][0]) + " " + channel + "/"

          else:
          #     channel = str(status[i][6])
                channel = ""
                modulation = ""


          #print i + 1,
          #print " = ",
          #print channel + " " + modulation 
          updatesql = "UPDATE status SET channel ='%s', modtype2 ='%s' WHERE id ='%i'" %(channel,modulation,(i+1))
          result = sql.qselect(updatesql)
          

        sql.close()

service()
"""       
SELECT c.sat,c.pol,c.frequency,c.symbolrate,c.rolloff,c.modulationtype,c.channel FROM channel_def c WHERE ((`channel_def.sat =\"" + str(status[i][1]) + "\") AND (c.pol =\"X\") AND (c.frequency =\"10969.0\") AND (c.symbolrate =\"6666.5\") AND (c.modulationtype = \"DVB-S\"))

SELECT `channel_def`.`channel`
FROM channel_def
WHERE ((`channel_def`.`sat` ="W3A") AND (`channel_def`.`pol` ="X") AND (`channel_def`.`frequency` ="10969.0") AND (`channel_def`.`symbolrate` ="6666.5") AND (`channel_def`.`modulationtype` = "DVB-S"))

"""
