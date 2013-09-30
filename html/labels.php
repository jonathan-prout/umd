<?php
 //usage: http://fxchange1.ebu.ch/umd/ird.php?sat=W3A

 //
 require_once('umd.common.php');
 require_once ('config.inc.php');
 dbstart();
 $sat = $_GET['sat'];
 

?>

<html>
 <head>
 <title>
  <?php 
 if ($sat == "")
	echo "All Receivers";
else
	echo $sat .' Receivers'
?>	
</title>

 <script>
<!--
function land(ref, target)
{
lowtarget=target.toLowerCase();
if (lowtarget=="_self") {window.location=loc;}
else {if (lowtarget=="_top") {top.location=loc;}
else {if (lowtarget=="_blank") {window.open(loc);}
else {if (lowtarget=="_parent") {parent.location=loc;}
else {parent.frames[target].location=loc;};
}}}
}
function jump(menu)
{
ref=menu.choice.options[menu.choice.selectedIndex].value;
splitc=ref.lastIndexOf("*");
target="";
if (splitc!=-1)
{loc=ref.substring(0,splitc);
target=ref.substring(splitc+1,1000);}
else {loc=ref; target="_self";};
if (ref != "") {land(loc,target);}
}
//-->
</script>
  </head>
 <body>
 <center>
 <?php
if ($_SERVER['REQUEST_METHOD'] == 'POST'){
	include("irdlabel.php");
}?>
 
 
 
 <?php 
 if ($sat == "")
	echo "All Receivers";
else
	echo $sat .' Receivers'
?>	
<table border="0"width="50%">
<tr>	
<td style="vertical-align:middle"> Select by category </td>
<td style="vertical-align:middle"> <form action="dummy" method="post"><select name="choice" size="1" onChange="jump(this.form)"><option value="#">Please Select</option><option value="labels.php?sat=W3A">W3A</option><option value="labels.php?sat=W2A">W2A</option><option value="labels.php?sat=NSS806">NSS806</option><option value="labels.php?sat=RX">HD Rx</option><option value="ird.php?sat=FiNE">FiNE</option></select></form></td>
</tr>
</table>
 </center>
 
 

 <table width="" height="*" border="1" cellpadding="1">
  <tr>
    <td><table width="400" height="382" border="1" cellpadding="1">
      <tr>
<form method="post" action="<?php echo $PHP_SELF; ?>">
          
     <?
	$sql = 'SELECT `status` . * , `equipment` . * , `status`.`channel` , `status`.`modtype2` '
        . ' FROM equipment, status'
        . ' WHERE (('
        . ' `equipment`.`id` = `status`.`id` '
        . ' ) AND ( `equipment`.`satellite` LIKE "%' 
		. $sat 
		. '%"))';
            //print $sql;
			
					
            $result = mysql_query($sql);
			$num=mysql_numrows($result);
			//print $num;
			//print $result;
	
	$i=0;
	$j=1;
	while ($i < $num) {
			
		$id=mysql_result($result,$i,"id");
		$name=mysql_result($result,$i,"labelnamestatic");
		$labeladdr=mysql_result($result,$i,"labeladdr");
		
		
			
			
			
		
		echo '<td><label>';
        echo $name;
		echo '<br />';
		?>
        <input type="text" name="label[]" id="<? echo $id; ?>" value="<? echo $name; ?>" />
		<input type ="hidden" name="IRD_number[]" value="<? echo $id; ?>" />
        <?  echo '</label></td>';
		if  ($j == 4){
			echo '</tr>';
			$j = 0;
			}
		
		$i++;
		$j++;
	}
	
	if ($j != 1)
		echo '</tr>';
		
	?>
</table>
<input type="hidden" name="numrows" value="<?php echo $num ?>" />
<input type="submit" value="Submit" /> 
</form>		
			
 </body>
 </html>

