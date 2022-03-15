<?php
 error_reporting(E_ALL); 
 ini_set( 'display_errors','1');

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

if ($mode == "json")
{
    header('Content-type: application/json');
 if ($doc == "multiviewer")
 {
  $sql = 'SELECT `id`,`Name` FROM `Multiviewer` WHERE 1';  
  $multiviewers = query($sql);
  echo json_encode(array_from_sql($multiviewers));
  
 }elseif  ($doc == "mv_input")
 {
  $sql = 'SELECT `PRIMARY`, `multiviewer`, `input` , `labeladdr1` , `labeladdr2` , `strategy` , `equipment` , `inputmtxid` , `inputmtxname` , `customlabel1`, `customlabel2` FROM `mv_input` WHERE 1';  
  $mv_input = query($sql);
  echo json_encode(array_from_sql($mv_input));
  
  }elseif  ($doc == "demods")
 {
 $sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE `isDemod`=1';
 $demods = query($sql);
 echo json_encode(array_from_sql($demods));
 
 }elseif  ($doc == "irds")
 {
 $sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE 1';
 $irds = query($sql);
 echo json_encode(array_from_sql($irds));
 
 }elseif  ($doc == "inpuutStrategies")
 {
 $sql = 'SELECT * FROM `inputStrategies`';
 $inpuutStrategies = query($sql);
 echo json_encode(array_from_sql($inpuutStrategies));
 }elseif  ($doc == "matrix_names") {
     $db = select_db("matrix");
     $sql = 'SELECT * FROM `matrixes`';
     $mtx_in = query($sql);
     $db = select_db("UMD");
     echo json_encode(array_from_sql($mtx_in));
 }elseif  ($doc == "matrix_in") {
     $db = select_db("matrix");
     $sql = 'SELECT * FROM `input`';
     $mtx_in = query($sql);
     $db = select_db("UMD");
     echo json_encode(array_from_sql($mtx_in));
 }elseif  ($doc == "equipment")
 {
    $sql = 'SELECT * FROM `equipment` WHERE 1';
    $irds = query($sql);
     echo json_encode(array_from_sql($irds));
 }elseif  ($doc == "matrix_out")
 {
 $db = select_db("matrix");
 $sql = 'SELECT * FROM `output`';
 $mtx_out = query($sql);
 $db = select_db("UMD");
 echo json_encode(array_from_sql($mtx_out));
 } else
 {
  echo "no doc parameter supplied";
 }
}else
{
    header('Content-type: text/javascript');
 $sql = 'SELECT `id`,`Name` FROM `Multiviewer` WHERE 1';  
 $multiviewers = query($sql);
 $sql = 'SELECT `PRIMARY`, `multiviewer`, `input` , `labeladdr1` , `labeladdr2` , 
       `strategy` , `equipment` , `inputmtxid` , `inputmtxname` , `customlabel1`, 
       `customlabel2` 
        FROM `mv_input` WHERE 1 
        order BY `input` ASC';

 $mv_input = query($sql);
 $sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE `isDemod`=1';
$demods = query($sql);
//$sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE 1';
$sql = 'SELECT * FROM `equipment` WHERE 1';
$irds = query($sql);
$sql = 'SELECT DISTINCT `sat` FROM `channel_def` WHERE 1';
$satlist = query($sql);
$sql = 'SELECT * FROM `inputStrategies`';
$inpuutStrategies = query($sql);
$db = select_db("matrix");
$sql = 'SELECT * FROM `input`';
$mtx_in = query($sql);
$mtx_in_sdi = query('SELECT * FROM `input` WHERE `matrixid` IN (SELECT `id` FROM `matrixes` where `capability` LIKE "%SDI%") AND `name` NOT LIKE "#%"');
$mtx_in_asi = query('SELECT * FROM `input` WHERE `matrixid` IN (SELECT `id` FROM `matrixes` where `capability` LIKE "%ASI%") AND `name`  LIKE "#%"');
$mtx_in_lband = query('SELECT * FROM `input` WHERE `matrixid` IN (SELECT `id` FROM `matrixes` where `capability` LIKE "%LBAND%")');

$sql = 'SELECT * FROM `output`';
$mtx_out = query($sql);

$mtx_out_sdi = query('SELECT * FROM `output` WHERE `matrixid` IN (SELECT `id` FROM `matrixes` where `capability` LIKE "%SDI%") AND `name` NOT LIKE "#%"');
$mtx_out_asi = query('SELECT * FROM `output` WHERE `matrixid` IN (SELECT `id` FROM `matrixes` where `capability` LIKE "%ASI%") AND `name`  LIKE "#%"');
$mtx_out_lband = query('SELECT * FROM `output` WHERE `matrixid` IN (SELECT `id` FROM `matrixes` where `capability` LIKE "%LBAND%")');
$mtx_names = query('SELECT `matrixes`.`id` , `matrixes`.`mtxName` FROM `matrixes`');
$db = select_db("UMD");


$search = array("\n", "\r", "\u", "\\t", "\t", "\f", "\b", "/", '\\');
$replace = array("", "", "", "", "","", "", "", "");

echo 'var multiviewers = JSON.parse('."'".str_replace($search, $replace, json_encode(array_from_sql($multiviewers)))."');\r\n";
echo 'var mv_input = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mv_input)))."');\r\n";
echo 'var demods = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($demods)))."');\r\n";
echo 'var irds = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($irds)))."');\r\n";
echo 'var inputStrategies = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($inpuutStrategies)))."');\r\n";
echo 'var mtx_in = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_in)))."');\r\n";
echo 'var mtx_in_sdi = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_in_sdi)))."');\r\n";
echo 'var mtx_in_asi = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_in_asi)))."');\r\n";
echo 'var mtx_in_lband = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_in_lband)))."');\r\n";
echo 'var mtx_out = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_out)))."');\r\n";
echo 'var mtx_out_sdi = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_out_sdi)))."');\r\n";
echo 'var mtx_out_asi = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_out_asi)))."');\r\n";
echo 'var mtx_out_lband = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_out_lband)))."');\r\n";
echo 'var matrix_names = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($mtx_names)))."');\r\n";


echo 'var satlist = JSON.parse('."'".str_replace($search, $replace,json_encode(array_from_sql($satlist)))."');\r\n";
}

function array_from_sql($sql_res): array
{

 
 $num_rows=mysqli_num_rows($sql_res);
  $res = array();
   $res = array_pad($res, $num_rows, 0);
 //echo $num_rows;
 for($x=0; $x < $num_rows; $x++ )
	{
	 //echo $x;
	 
	 $row = mysqli_fetch_assoc($sql_res);
	 //echo implode($row);
	  //$row = mysqli_fetch_array($result, mysqli_NUM)
	 $res[$x] =  $row;
	//}
	//$src_dest[row[0]][] = $row[1];
	
	}
	return $res;
}


function ird_dropdown($curval): string
{
 global $irds;
 $rval = "";
 $num_rows= mysqli_num_rows($irds);
 for($x=0; $x < $num_rows; $x++ ){
	   $valID=mysqli_result($irds,$x,"id");
	   $description=mysqli_result($irds,$x,"labelnamestatic");
	   if ($curval == $valID)
		$rval = $rval.'<option value="'.$valID.'" selected>'.$description.'</option>';
	   else
		$rval = $rval.'<option value="'.$valID.'">'.$description.'</option>';
	   }
	 return $rval;
}

function mtx_in_dropdown($curval): string
{
 global $mtx_in;
 $rval = "";
 $num_rows=mysqli_num_rows($mtx_in);
 for($x=0; $x < $num_rows; $x++ ){
	   $name=mysqli_result($mtx_in,$x,"name");
	   if ($curval == $name)
		$rval = $rval.'<option value="'.$name.'" selected>'.$name.'</option>';
	   else
		$rval = $rval.'<option value="'.$name.'">'.$name.'</option>';
	   }
	 return $rval;
}
function mtx_out_dropdown($curval): string
{
 global $mtx_out;
 $rval = "";
 $num_rows=mysqli_num_rows($mtx_out);
 for($x=0; $x < $num_rows; $x++ ){
	   $name=mysqli_result($mtx_out,$x,"name");
	   if ($curval == $name)
		$rval = $rval.'<option value="'.$name.'" selected>'.$name.'</option>';
	   else
		$rval = $rval.'<option value="'.$name.'">'.$name.'</option>';
	   }
	   return $rval;
	   
	 
}

function input_strategy_dropdown($curval): string
{
 global $inpuutStrategies;
 $rval = "";
 $num_rows=mysqli_num_rows($inpuutStrategies);
 for($x=0; $x < $num_rows; $x++ ){
	   $valID=mysqli_result($inpuutStrategies,$x,"PRIMARY");
	   $description=mysqli_result($inpuutStrategies,$x,"description");
	   if ($curval == $valID)
		$rval = $rval.'<option value="'.$valID.'" selected>'.$description.'</option>';
	   else
		$rval = $rval.'<option value="'.$valID.'">'.$description.'</option>';
	   }
	 return $rval;
}


/**
 * @param $mvid
 * @return false|mixed|string|null
 */
function get_mv_name($mvid):string
{
  global $multiviewers;

  $num_rows=mysqli_num_rows($multiviewers);
  
  for($x=0; $x < $num_rows; $x++ ){
	 $id=mysqli_result($multiviewers,$x,"id");
	 $name=mysqli_result($multiviewers,$x,"Name");
	 
	 if ($id == $mvid)
	  return $name;
	 else
	  continue;
  
  }
  return "";
}
dbend();




