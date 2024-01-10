#!/opt/ebu/py37/bin/python 
import sys

try:
    import cgi, os
    import json
    import cgitb;

    cgitb.enable()
    import mysql, threading
except ImportError as e:
    print(str(e))
    sys.exit(1)

mysql.mysql.semaphore = threading.BoundedSemaphore(value=1)
mysql.mysql.mutex = threading.RLock()
mysql.mysql.dname = "matrix"
sql = mysql.mysql()

dest_src = {}
src_dest = {}

for row in sql.qselect("SELECT `status`.`input`, `status`.`output` FROM `status` WHERE (`status`.`matrixid` =1);"):
    s = int(row[0])
    d = int(row[1])
    dest_src[d] = s
    if not src_dest.has_key(s):
        src_dest[s] = []
    src_dest[s].append(d)

inputMap = {}
for row in sql.qselect("SELECT `input`.`name` , `input`.`port` FROM `input`WHERE (`input`.`matrixid` =1)"):
    n = row[0]
    p = int(row[1])
    inputMap[p] = n
outputMap = {}
for row in sql.qselect("SELECT `output`.`name` , `output`.`port` FROM `output`WHERE (`output`.`matrixid` =1)"):
    n = row[0]
    p = int(row[1])
    outputMap[p] = n

print("Content-Type: text/html")
print("")

print("""<!DOCTYPE html>
<html>
	<head>
<style>
table, th, td {
    border: 1px solid black;
    border-collapse:collapse;
}
th, td {
    padding: 5px;
}
</style>
</head>
<body>

<form id="frm1" action="#">
Search: <input type="text" name="lname" value="" onkeyup="myFunction()"><br><br>

</form> 



<button onclick="myFunction()">Filter</button>

<p id="demo"></p>

<script> """)

print("var dest_src = " + json.dumps(dest_src) + ";")

print("var src_dest = " + json.dumps(src_dest) + ";")

print("var inputMap = " + json.dumps(inputMap) + ";")

print("var outputMap = " + json.dumps(outputMap) + ";")

print("")

print("""function myFunction() {
    var x = document.getElementById("frm1");
    var text = "";
    var i;
    for (i = 0; i < x.length ;i++) {
        text += x.elements[i].value + "<br>";
    }
	
		
	text +="<table><tr><th>Source</th><th>Dest</th></tr>";
	
	for (var key in dest_src)
	{
	  if (dest_src.hasOwnProperty(key))
	  {
		var inName = "";
		outName = outputMap[key];
		if(typeof outName === 'undefined'){
		  continue
			};
		if ((outName.search(x.elements[0].value) != -1)){
		 text +="<tr><td>";
		text += inputMap[dest_src[key]] + "</td><td>";
		
			//text +="<td>";
			text += outName;
			
			
		text +="</td></tr>";
	  }
	  }
	}
	  
	  //text +=att.getNamedItem("name").nodeValue;
	  
	  //text +=att.getNamedItem("ip").nodeValue;
	  //text +="</td><td>";
	  //text +=att.getNamedItem("InUse").nodeValue;
	  //text +="</td></tr>";
	  
	text +="</table>";
		document.getElementById("demo").innerHTML = text;
}
</script>""")
