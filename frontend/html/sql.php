<?php
 $dbhost = '172.17.0.2';
 $dbport = 3306;
 $dblogin= 'umd';
 $dbpass = 'umd';
 $dbname ='UMD';
 $t_bandwidths='';
 $connection='';
 
                                                                                                                               
 
 function dbstart(){
 	global $dbhost,$dblogin,$dbpass,$dbname, $dbport, $connection;
 	//echo($dbhost.$dblogin.$dbpass.$dbname.$dbport);
 	$connection = mysqli_connect("$dbhost","$dblogin","$dbpass", "UMD", 3306, ) or die ("Failure with the UMD manager database. Please restart machine.");
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


