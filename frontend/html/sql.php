<?php
 $dbhost = '127.0.0.1';
 $dbport = 3306;
 $dblogin= 'umd';
 $dbpass = 'umd';
 $dbname ='UMD';
 $t_bandwidths='';
 $connection='';

 function dbfail($message){
     error_log($message);
     header($_SERVER['SERVER_PROTOCOL'] . ' 500 Internal Server Error', true, 500);
     die($message);
 }
                                                                                                                               
 
 function dbstart(){
 	global $dbhost,$dblogin,$dbpass,$dbname, $dbport, $connection;
 	//echo($dbhost.$dblogin.$dbpass.$dbname.$dbport);
 	$connection = mysqli_connect("$dbhost","$dblogin","$dbpass", "UMD", 3306, ) or dbfail ("Failure with the UMD manager database. Please restart machine.");
 	$db = mysqli_select_db($connection, $dbname);
 }

function dbend(){
 	global $connection;
 	mysqli_close($connection);
 }

function mysqli_result($res,$row=0,$col=0){
    $numrows = mysqli_num_rows($res);
    if ($numrows && $row <= ($numrows-1) && $row >=0){
        mysqli_data_seek($res,$row);
        $resrow = (is_numeric($col)) ? mysqli_fetch_row($res) : mysqli_fetch_assoc($res);
        if (isset($resrow[$col])){
            return $resrow[$col];
        }
    }
    return false;
}

function select_db($name): bool
{
    global $connection;
    return mysqli_select_db($connection, $name);
}

/**
 * @param $sql
 * @return bool|mysqli_result
 */
function query($sql)
{
    global $connection;
    return mysqli_query($connection, $sql);
}


