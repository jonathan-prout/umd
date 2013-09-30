<?
 $dbhost = 'localhost';
 $dblogin= 'umd';
 $dbpass = 'umd';
 $dbname ='UMD';
 $t_bandwidths='';
 $connection='';
 
 $kaleidoconv = array(1 => "192.168.3.51",
                      2 => "192.168.3.52",
                      3 => "192.168.3.53",
                      4 => "192.168.3.54",
                      5 => "192.168.3.55",
                      6 => "192.168.3.56",
                      7 => "192.168.3.57",
                      8 => "192.168.3.58",
                      9 => "192.168.3.59");                                                                                                                                    
 
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
