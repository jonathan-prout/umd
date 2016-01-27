<?php
 error_reporting(E_ALL); 
 ini_set( 'display_errors','1');
 require_once('umd.common.php');
 require_once ('sql.php');
 dbstart();
if(isset($_GET['mode']))
{
$mode = $_GET['mode'];

}else{
 $mode = "";

}

if(isset($_GET['doc']))
{
$doc = $_GET['doc'];
}else{
 $doc = "";
}

$search = array("\n", "\r", "\u", "\\t", "\t", "\f", "\b", "/", '\\');
$replace = array("", "", "", "", "","", "", "", "");

if ($mode == "json")
{
 if ($doc == "multiviewer")
 {
  $sql = 'SELECT `id`,`Name` FROM `Multiviewer` WHERE 1';  
  $multiviewers = mysql_query($sql);
  echo json_encode(array_from_sql($multiviewers));
  
 }elseif  ($doc == "mv_input")
 {
  $sql = 'SELECT `PRIMARY`, `multiviewer`, `input` , `labeladdr1` , `labeladdr2` , `strategy` , `equipment` , `inputmtxid` , `inputmtxname` , `customlabel1`, `customlabel2` FROM `mv_input` WHERE 1';  
  $mv_input = mysql_query($sql);
  echo json_encode(array_from_sql($mv_input));
  
  }elseif  ($doc == "demods")
 {
 $sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE `isDemod`=1';
 $demods = mysql_query($sql);
 echo json_encode(array_from_sql($demods));
 
 }elseif  ($doc == "irds")
 {
 $sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE 1';
 $irds = mysql_query($sql);
 echo json_encode(array_from_sql($irds));
 
 }elseif  ($doc == "inpuutStrategies")
 {
 $sql = 'SELECT * FROM `inputStrategies`';
 $inpuutStrategies = mysql_query($sql);
 echo json_encode(array_from_sql($inpuutStrategies));
 
 }elseif  ($doc == "matrix_in")
 {
 $ressource = mysql_select_db("matrix");
 $sql = 'SELECT * FROM `input`';
 $mtx_in = mysql_query($sql);
 $ressource = mysql_select_db("umd");
  echo 'var mtx_in = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_in)))."');\r\n";
  
 }elseif  ($doc == "matrix_names")
 {
 $ressource = mysql_select_db("matrix");
 $sql = 'SELECT `matrixes`.`id` , `matrixes`.`mtxName` FROM `matrixes`';
 $mtx_out = mysql_query($sql);
 $ressource = mysql_select_db("umd");
 echo 'var matrix_names = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_out)))."');\r\n";
 
 }elseif  ($doc == "matrix_out")
 {
 $ressource = mysql_select_db("matrix");
 $sql = 'SELECT * FROM `output`';
 $mtx_out = mysql_query($sql);
 $ressource = mysql_select_db("umd");
 echo 'var mtx_out = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_out)))."');\r\n";
 } else
 {
  echo "no doc parameter supplied";
 }
}else
{
 $sql = 'SELECT `id`,`Name` FROM `Multiviewer` WHERE 1';  
 $multiviewers = mysql_query($sql);
 $sql = 'SELECT `PRIMARY`, `multiviewer`, `input` , `labeladdr1` , `labeladdr2` , `strategy` , `equipment` , `inputmtxid` , `inputmtxname` , `customlabel1`, `customlabel2` FROM `mv_input` WHERE 1';  
 $mv_input = mysql_query($sql);
 $sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE `isDemod`=1';
$demods = mysql_query($sql);
//$sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE 1';
$sql = 'SELECT * FROM `equipment` WHERE 1';
$irds = mysql_query($sql);
$sql = 'SELECT DISTINCT `sat` FROM `channel_def` WHERE 1';
$satlist = mysql_query($sql);
$sql = 'SELECT * FROM `inputStrategies`';
$inpuutStrategies = mysql_query($sql);
$ressource = mysql_select_db("matrix");
//$sql = 'SELECT * FROM `input`';
//$mtx_in = mysql_query($sql);
$mtx_in_sdi = mysql_query('SELECT * FROM `input` WHERE `matrixid` =(SELECT `id` FROM `matrixes` where `capability` LIKE "%SDI%") AND `name` NOT LIKE "#%"');
$mtx_in_asi = mysql_query('SELECT * FROM `input` WHERE `matrixid` =(SELECT `id` FROM `matrixes` where `capability` LIKE "%ASI%") AND `name`  LIKE "#%"');
$mtx_in_lband = mysql_query('SELECT * FROM `input` WHERE `matrixid` =(SELECT `id` FROM `matrixes` where `capability` LIKE "%LBAND%")');
$ressource = mysql_select_db("umd");
$ressource = mysql_select_db("matrix");

$mtx_out_sdi = mysql_query('SELECT * FROM `output` WHERE `matrixid` =(SELECT `id` FROM `matrixes` where `capability` LIKE "%SDI%") AND `name` NOT LIKE "#%"');
$mtx_out_asi = mysql_query('SELECT * FROM `output` WHERE `matrixid` =(SELECT `id` FROM `matrixes` where `capability` LIKE "%ASI%") AND `name`  LIKE "#%"');
$mtx_out_lband = mysql_query('SELECT * FROM `output` WHERE `matrixid` =(SELECT `id` FROM `matrixes` where `capability` LIKE "%LBAND%")');
$mtx_names = mysql_query('SELECT `matrixes`.`id` , `matrixes`.`mtxName` FROM `matrixes`');
$ressource = mysql_select_db("umd");




echo 'var multiviewers = JSON.parse('."'".str_replace($search, $replace, json_encode(array_from_sql($multiviewers)))."');\r\n";
echo 'var mv_input = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mv_input)))."');\r\n";
echo 'var demods = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($demods)))."');\r\n";
echo 'var irds = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($irds)))."');\r\n";
echo 'var inputStrategies = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($inpuutStrategies)))."');\r\n";
echo 'var mtx_in_sdi = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_in_sdi)))."');\r\n";
echo 'var mtx_in_asi = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_in_asi)))."');\r\n";
echo 'var mtx_in_lband = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_in_lband)))."');\r\n";
echo 'var mtx_out_sdi = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_out_sdi)))."');\r\n";
echo 'var mtx_out_asi = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_out_asi)))."');\r\n";
echo 'var mtx_out_lband = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_out_lband)))."');\r\n";
echo 'var mtx_names = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_names)))."');\r\n";
echo 'var satlist = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($satlist)))."');\r\n";
}

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

