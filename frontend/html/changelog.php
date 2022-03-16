<?php
 error_reporting(E_ALL); 
 ini_set( 'display_errors','1');
 require_once('umd.common.php');
 require_once ('sql.php');
 dbstart();
 $ressource = select_db("matrix");
function array_from_sql($sql_res)
{

 
 $numrows=mysqli_num_rows($sql_res);
  $res = array();
   $res = array_pad($res, $numrows, 0);
 //echo $numrows;
 for($x=0; $x < $numrows; $x++ )
	{
	 //echo $x;
	 
	 $row = mysqli_fetch_assoc($sql_res);
	 //echo implode($row);
	  //$row = mysql_fetch_array($result, MYSQL_NUM)
	 $res[$x] =  $row;
	//}
	//$src_dest[row[0]][] = $row[1];
	
	}
	return $res;
}

$search = array("\n", "\r", "\u", "\\t", "\t", "\f", "\b", "/", '\\');
$replace = array("", "", "", "", "","", "", "", "");

if(isset($_GET['mtx']))
{
    $mtx = intval($_GET['mtx']);

    if(isset($_GET['in']))
    {
        $in = intval($_GET['in']);
        $sql ='SELECT * FROM `changelog` WHERE `matrixid` ='.$mtx.' AND  `input` ='.$in.' ORDER BY `time` DESC;';
		$arr = array_from_sql(query($sql));
    }else if(isset($_GET['out']))
    {
        $out = intval($_GET['out']);
        $sql ='SELECT * FROM `changelog` WHERE `matrixid` ='.$mtx.' AND  `output` ='.$out.' ORDER BY `time` DESC;';
		$arr = array_from_sql(query($sql));
    
    }else{
        $arr = ["in out out not supplied"];
		
    }
	
    
    
}else{
$arr = ["matrix not supplied"];

}


echo str_replace($search, $replace,json_encode($arr));
dbend();
?>