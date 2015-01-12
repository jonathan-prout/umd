<?php
  //error_reporting(E_ERROR | E_WARNING | E_PARSE);
  error_reporting(E_ALL);
 ini_set( 'display_errors','1'); 


 
 //usage: http://fxchange1.ebu.ch/umd/ird.php?sat=W3A

 //
   require_once("xajax/xajax.inc.php");
  session_start();
 
  $dbhost = 'localhost';
 $dblogin= 'umd';
 $dbpass = 'umd';
 $dbname ='matrix';
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
 
 dbstart();
 //$filter = $_GET['filter'];
 $mtx = $_GET['mtx'];

 $sql = 'SELECT `status`.`input`, `status`.`output` FROM `status` WHERE (`status`.`matrixid` ='.$mtx.');';
		
		//print $sql;
		
		
            $result = mysql_query($sql);
			$num=mysql_numrows($result);
			//print $num;
	//echo $result;
	$dest_src = array();
	$src_dest = array();
	$i=0;
	while ($row = mysql_fetch_array($result, MYSQL_NUM))
	{
	  //$row = mysql_fetch_array($result, MYSQL_NUM)
	$d = 0 +$row[1];
	$dest_src[$d] = $row[0];
	//echo "row ".$row[1]."->".$row[0];
	//if ($src_dest[row[0]] == "" )
	//{
	  $src_dest[row[0]] = array();
	//}
	//$src_dest[row[0]][] = $row[1];
	$i++;
	}
	echo 'var dest_src = '.json_encode($dest_src);
	echo 'var src_dest = '.json_encode($src_dest);
?>


