<?php
 error_reporting(E_ALL); 
 ini_set( 'display_errors','1');
 require_once('umd.common.php');
 require_once ('sql.php');
 dbstart();


$sql = 'SELECT `id`,`Name` FROM `Multiviewer` WHERE 1';  
$multiviewers = mysql_query($sql);


$sql = 'SELECT `PRIMARY`, `multiviewer`, `input` , `labeladdr1` , `labeladdr2` , `strategy` , `equipment` , `inputmtxid` , `inputmtxname` , `customlabel1`, `customlabel2` FROM `mv_input` WHERE 1';  
$mv_input = mysql_query($sql);
$sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE `isDemod`=1';
$demods = mysql_query($sql);
$sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE 1';
$irds = mysql_query($sql);
$sql = 'SELECT * FROM `inputStrategies`';
$inpuutStrategies = mysql_query($sql);



$ressource = mysql_select_db("matrix");
$sql = 'SELECT * FROM `input`';
$mtx_in = mysql_query($sql);
$sql = 'SELECT * FROM `output`';
$mtx_out = mysql_query($sql);
$ressource = mysql_select_db("umd");
//echo "something";
//echo mysql_fetch_array($multiviewers);
echo 'var multiviewers = '.json_encode(array_from_sql($multiviewers));
echo 'var mv_input = '.json_encode(array_from_sql($mv_input));
echo 'var demods = '.json_encode(array_from_sql($demods));
echo 'var irds = '.json_encode(array_from_sql($irds));
echo 'var inpuutStrategies = '.json_encode(array_from_sql($inpuutStrategies));
echo 'var mtx_in = '.json_encode(array_from_sql($mtx_in));
echo 'var mtx_out = '.json_encode(array_from_sql($mtx_out));


function array_from_sql($sql_res)
{

 
 $numrows=mysql_numrows($sql_res);
  $res = array();
   $res = array_pad($res, $numrows, 0);
 //echo $numrows;
 for($x=0; $x < $numrows; $x++ )
	{
	 //echo $x;
	 
	 $row = mysql_fetch_assoc($sql_res);
	 //echo implode($row);
	  //$row = mysql_fetch_array($result, MYSQL_NUM)
	 $res[$x] =  $row;
	//}
	//$src_dest[row[0]][] = $row[1];
	
	}
	return $res;
}


function ird_dropdown($curval)
{
 global $irds;
 $rval = "";
 $numrows=mysql_numrows($irds);
 for($x=0; $x < $numrows; $x++ ){
	   $valID=mysql_result($irds,$x,"id");
	   $description=mysql_result($irds,$x,"labelnamestatic");
	   if ($curval == $valID)
		$rval = $rval.'<option value="'.$valID.'" selected>'.$description.'</option>';
	   else
		$rval = $rval.'<option value="'.$valID.'">'.$description.'</option>';
	   }
	 return $rval;
}

function mtx_in_dropdown($curval)
{
 global $mtx_in;
 $rval = "";
 $numrows=mysql_numrows($mtx_in);
 for($x=0; $x < $numrows; $x++ ){
	   $name=mysql_result($mtx_in,$x,"name");
	   if ($curval == $name)
		$rval = $rval.'<option value="'.$name.'" selected>'.$name.'</option>';
	   else
		$rval = $rval.'<option value="'.$name.'">'.$name.'</option>';
	   }
	 return $rval;
}
function mtx_out_dropdown($curval)
{
 global $mtx_out;
 $rval = "";
 $numrows=mysql_numrows($mtx_out);
 for($x=0; $x < $numrows; $x++ ){
	   $name=mysql_result($mtx_out,$x,"name");
	   if ($curval == $name)
		$rval = $rval.'<option value="'.$name.'" selected>'.$name.'</option>';
	   else
		$rval = $rval.'<option value="'.$name.'">'.$name.'</option>';
	   }
	   return $rval;
	   
	 
}

function input_strategy_dropdown($curval)
{
 global $inpuutStrategies;
 $rval = "";
 $numrows=mysql_numrows($inpuutStrategies);
 for($x=0; $x < $numrows; $x++ ){
	   $valID=mysql_result($inpuutStrategies,$x,"PRIMARY");
	   $description=mysql_result($inpuutStrategies,$x,"description");
	   if ($curval == $valID)
		$rval = $rval.'<option value="'.$valID.'" selected>'.$description.'</option>';
	   else
		$rval = $rval.'<option value="'.$valID.'">'.$description.'</option>';
	   }
	 return $rval;
}


function get_mv_name($mvid)
{
  global $multiviewers;
  $rval = "";
  $numrows=mysql_numrows($multiviewers);
  
  for($x=0; $x < $numrows; $x++ ){
	 $id=mysql_result($multiviewers,$x,"id");
	 $name=mysql_result($multiviewers,$x,"Name");
	 
	 if ($id == $mvid)
	  return $name;
	 else
	  continue;
  
  }
  
}
dbend();

?>

