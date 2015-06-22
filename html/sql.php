<?
 $dbhost = 'localhost';
 $dblogin= 'umd';
 $dbpass = 'umd';
 $dbname ='UMD';
 $t_bandwidths='';
 $connection='';
 
                                                                                                                               
 
 function dbstart(){
 	global $dbhost,$dblogin,$dbpass,$dbname,$connection;
 	
 	$connection = mysql_connect("$dbhost","$dblogin","$dbpass") or die ("Failure with the UMD manager database. Please restart machine.");
 	$ressource = mysql_select_db($dbname);
 }

function dbend(){
 	global $connection;
 	mysql_close($connection);
 }
 


 ?>
