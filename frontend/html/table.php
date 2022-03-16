<?php
 error_reporting(E_ALL); 
 ini_set( 'display_errors','1');
?>



<?php

$sql = 'SELECT `id`,`Name` FROM `Multiviewer` WHERE 1';  
$multiviewers = mysql_query($sql);

if ($mv == "")
$sql = 'SELECT `PRIMARY`, `multiviewer`, `input` , `labeladdr1` , `labeladdr2` , `strategy` , `equipment` , `inputmtxid` , `inputmtxname` , `customlabel1`, `customlabel2` FROM `mv_input` WHERE 1';  
else
$sql = 'SELECT `PRIMARY`, `multiviewer`, `input` , `labeladdr1` , `labeladdr2` , `strategy` , `equipment` , `inputmtxid` , `inputmtxname` , `customlabel1`, `customlabel2` FROM `mv_input` WHERE `multiviewer` ='.$mv;  
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
?>


<h3>Eurovision UMD Manager: Labels</h3>


<td style="vertical-align:middle"> Select by category </td>
<td style="vertical-align:middle"> <form action="dummy" method="post">
<input type="hidden" name="formused" value="table">
<select name="choice" size="1" onChange="jump(this.form)"><option value="#">Please Select</option>

<?
            
			$rows=mysql_numrows($multiviewers);
			$i=0;
			while ($i < $rows) {
			$id=mysql_result($multiviewers,$i,"id");
			$name=mysql_result($multiviewers,$i,"Name");
			
			echo '<option value="mv='.$id.'">'.$name.'</option>';
			$i++;
			}
?>
</select>
</form></td>

 <form method="post" action="<?php echo $_SERVER['PHP_SELF'];?>">
<input type="hidden" name="formused" value="table">
<table width="" height="*" border="1" cellpadding="1">
  <tr>
    <td>Multiviewer Name</td><td>Input</td><td>strategy</td><td>equipment</td><td>input matrix</td><td>matrix input</td><td>custom top</td><td>custom bottom</td>
  </tr>
<?
if ($mv == "")
  echo '<tr>
    <td>Multiviewer not selected</td></tr>';
else
 {
 $numrows=mysql_numrows($mv_input);
  for($i=0; $i < $numrows; $i++ ){
	$PRIMARY				= mysql_result($mv_input,$i,"PRIMARY");
	$multiviewer			= mysql_result($mv_input,$i,"multiviewer");
	$input				= mysql_result($mv_input,$i,"input");
	$labeladdr1			= mysql_result($mv_input,$i,"labeladdr1");
	$labeladdr2			= mysql_result($mv_input,$i,"labeladdr2");
	$strategy				= mysql_result($mv_input,$i,"strategy");
	$equipment			= mysql_result($mv_input,$i,"equipment");
	$inputmtxid			= mysql_result($mv_input,$i,"inputmtxid");
	$inputmtxname			= mysql_result($mv_input,$i,"inputmtxname");
	$customlabel1			= mysql_result($mv_input,$i,"customlabel1");
	$customlabel2			= mysql_result($mv_input,$i,"customlabel2");
	echo '<tr id='.$PRIMARY.'>';
	echo '<td>'.get_mv_name($multiviewer).'</td>';
	echo '<td>'.$input.'</td>';
	echo '<td><select name="strategy'.$PRIMARY.'">'.input_strategy_dropdown($strategy).'</select></td>';
	echo '<td><select name="equipment'.$PRIMARY.'"> <option value="">No Equipment</option>'.ird_dropdown($equipment).'</select></td>';
	echo '<td><select name="matrix'.$PRIMARY.'"> <option value="">No Matrix</option>';
	if ($inputmtxid == 1)
	 echo '<option value="1" selected>EVC GVG MATRIX</option></select></td>';
	else
	 echo '<option value="1">EVC GVG MATRIX</option></select></td>';
	echo '<td><select name="mtxIn'.$PRIMARY.'"> <option value="">No Matrix Input</option>'.mtx_out_dropdown($inputmtxname).'</select></td>';
	echo '<td><input type="text" name="top'.$PRIMARY.'" id="top'.$PRIMARY.'" value="'.$customlabel1.'>" /></td>';
	echo '<td><input type="text" name="bottom'.$PRIMARY.'" id="bottom'.$PRIMARY.'" value="'.$customlabel2.'>" /></td>';
	echo '</tr>';
  }
 }
?>
	
</table>
			

<input type="submit" value="Submit"> 


           </form>
        </div>
     
     
     </div>
     
     <div id="outputDiv">
     	
     </div>

 </body>