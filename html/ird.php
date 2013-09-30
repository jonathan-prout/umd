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
 if ($sat == "")
	echo "All Receivers";
else
	echo $sat .' Receivers'
?>	
<table border="0"width="50%">
<tr>	
<td style="vertical-align:middle"> Select by category </td>
<td style="vertical-align:middle"> <form action="dummy" method="post"><select name="choice" size="1" onChange="jump(this.form)"><option value="#">Please Select</option><option value="ird.php?sat=W3A">W3A</option><option value="ird.php?sat=W2A">W2A</option><option value="ird.php?sat=NSS806">NSS806</option><option value="ird.php?sat=RX">HD Rx</option><option value="ird.php?sat=FiNE">FiNE</option></select></form></td>
</tr>
</table>
 </center>
 <table border="1" bordercolor="grey" style="background-color:lightgrey" width="90%" cellpadding="3" cellspacing="3">
	<tr>
		<td>IRD</td>
		<td>Current Channel</td>
		<td>Modulation</td>
		<td>Video Format</td>
		<td>Service</td>
	</tr>
	
	


<?php 
	
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
		
	
	$i=0;
	while ($i < $num) {
		$label=mysql_result($result,$i,"labelnamestatic");
		$channel=mysql_result($result,$i,"channel");
		$modulation=mysql_result($result,$i,"modtype2");
		$videoresolution=mysql_result($result,$i,"videoresolution");
		$aspectratio=mysql_result($result,$i,"aspectratio");
		$servicename=mysql_result($result,$i,"servicename");
		$ip=mysql_result($result,$i,"ip");
		$videostate=mysql_result($result,$i,"videostate");
		$framerate=mysql_result($result,$i,"framerate");
		
		if ($videostate == "Running")
			$background = "lightgreen";
		else
			$background = "99FFFF";
			
		echo '<tr>';
		echo '<td bgcolor="'. $background .'"><a href ="http://'. $ip . '/" target=_blank>'. $label .'</a></td>';
		echo '<td bgcolor="'. $background .'">'. $channel . '</td>';
		echo '<td bgcolor="'. $background .'">'. $modulation . '</td>';
		echo '<td bgcolor="'. $background .'">'. $videoresolution . ', '. $aspectratio .', '. $framerate . '</td>';
		echo '<td bgcolor="'. $background .'">'. $servicename . '</td>';
		echo '</tr>';
	
	
	$i++;
	}
	
	
		
 ?>
 </table>