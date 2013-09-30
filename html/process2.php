<?php


 $label1=$_POST['label1']; 
 $label2=$_POST['label2']; 
 $label3=$_POST['label3']; 
 $label4=$_POST['label4']; 
 $label5=$_POST['label5']; 
 $label6=$_POST['label6']; 
 $label7=$_POST['label7']; 
 $label8=$_POST['label8']; 
 $label9=$_POST['label9']; 
 $label10=$_POST['label10']; 
 $label11=$_POST['label11']; 
 $label12=$_POST['label12']; 
 $label13=$_POST['label13']; 
 $label14=$_POST['label14']; 
 $label15=$_POST['label15']; 
 $label16=$_POST['label16']; 
 ?>
 

 <p>Updating Labels...

 <?
mysql_select_db("UMD") or die(mysql_error()); 
mysql_query("UPDATE customlabel SET text = '$label1' WHERE customlabel.id ='1' "); 
mysql_query("UPDATE customlabel SET text = '$label2' WHERE customlabel.id ='2' "); 
mysql_query("UPDATE customlabel SET text = '$label3' WHERE customlabel.id ='3' "); 
mysql_query("UPDATE customlabel SET text = '$label4' WHERE customlabel.id ='4' "); 
mysql_query("UPDATE customlabel SET text = '$label5' WHERE customlabel.id ='5' "); 
mysql_query("UPDATE customlabel SET text = '$label6' WHERE customlabel.id ='6' "); 
mysql_query("UPDATE customlabel SET text = '$label7' WHERE customlabel.id ='7' "); 
mysql_query("UPDATE customlabel SET text = '$label8' WHERE customlabel.id ='8' "); 
mysql_query("UPDATE customlabel SET text = '$label9' WHERE customlabel.id ='9' "); 
mysql_query("UPDATE customlabel SET text = '$label10' WHERE customlabel.id ='10' "); 
mysql_query("UPDATE customlabel SET text = '$label11' WHERE customlabel.id ='11' "); 
mysql_query("UPDATE customlabel SET text = '$label12' WHERE customlabel.id ='12' "); 
mysql_query("UPDATE customlabel SET text = '$label13' WHERE customlabel.id ='13' "); 
mysql_query("UPDATE customlabel SET text = '$label14' WHERE customlabel.id ='14' "); 
mysql_query("UPDATE customlabel SET text = '$label15' WHERE customlabel.id ='15' "); 
mysql_query("UPDATE customlabel SET text = '$label16' WHERE customlabel.id ='16' "); 


$command = "../programming/client/customlabel.py";
$output = array();
$return_var = 0;
exec($command, $output, $return_var);

if ($return_var == 0)
	echo "done";
else
	echo "error";