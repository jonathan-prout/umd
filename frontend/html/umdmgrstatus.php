<?php
 error_reporting(E_ALL); 
 ini_set( 'display_errors','1'); 


 
 //usage: http://fxchange1.ebu.ch/umd/ird.php?sat=W3A

 //
 require_once('umd.common.php');
 require_once ('sql.php');
 dbstart();

 

?>

<html>
 <head>
  <meta http-equiv="refresh" content="60">
 <title>UMD Manager Status</title>

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
<font size="+1">UMD Manager Status at <?php echo date('G'), ":", date('i'), ":", date('s')  ?></font><br /><br />


 <?php 
	
	$sql = "SELECT * FROM `management`" ;
		
		//print $sql;
		
		
            $result = query($sql);
			$num=mysqli_num_rows($result);
			//print $num;
		
	
	$i=0;
	$mgmt = array();
	while ($i < $num) {
		$key=mysqli_result($result,$i,"key");
		$value=mysqli_result($result,$i,"value");
		$mgmt[$key] = $value;
		$i++;
	}
     ?>
	
	

 
 
 
 
 
  <table border="1" bordercolor="grey" style="background-color:lightgrey"  cellpadding="3" cellspacing="3">
	<tr>
		<td>Equipment Polling</td>
		<?php if ($mgmt["current_status"] == "RUNNING")
			{$background = "lightgreen";}
		elseif 	($mgmt["current_status"] == "STARTING")
		{$background = "yellow";}
		elseif 	($mgmt["current_status"] == "OFFLINE_ERROR")
		{$background = "red";}
		else
			$background = "99FFFF";
			
		
		echo '<td bgcolor="'. $background .'">'. $mgmt["current_status"] .'</td>';
		?>
	       
	</tr>
	<tr>
		<td>Running Since</td>
		<?php 
		$background = "99FFFF";
			
		
		echo '<td bgcolor="'. $background .'">'. $mgmt["up_since"] .'</td>';
		?>
	       
	</tr>
		<tr>
		<td>Last Self check</td>
		<?php 
		$background = "99FFFF";
			
		
		echo '<td bgcolor="'. $background .'">'. $mgmt["last_self_check"] .'</td>';
		?>
	       
	</tr>
	<tr>
		<td>Average time taken to poll equipment</td>
		<?php if ($mgmt["avg_jitter"] < 5)
			{$background = "lightgreen";}
		elseif 	($mgmt["avg_jitter"] < 10)
		{$background = "yellow";}
		
		
		else
			{$background = "red";}
			
		
		echo '<td bgcolor="'. $background .'">'. $mgmt["avg_jitter"] .' seconds</td>';
		?>
		</tr>
		<tr>
		<td>Number of offline equipment</td>
		<?php if ($mgmt["equipment_offline"] < 10)
			{$background = "lightgreen";}
		elseif 	($mgmt["equipment_offline"] < 30)
		{$background = "yellow";}
		
		
		else
			{$background = "red";}
			
		
		echo '<td bgcolor="'. $background .'">'. $mgmt["equipment_offline"] .'</td>';
		?>
	       
	</tr>       
	</tr>
		<tr>
		<td>Number of errors</td>
		<?php if ($mgmt["errors"] < 1)
			{$background = "lightgreen";}
		elseif 	($mgmt["errors"] < 3)
		{$background = "yellow";}
		
		
		else
			{$background = "red";}
			
		
		echo '<td bgcolor="'. $background .'">'. $mgmt["errors"] .'</td>';
		?>
		

	       
	</tr>
	
		<tr>
		<td>Equipment starting</td>
		<?php if ($mgmt["STAT_INIT"] < 10)
			{$background = "lightgreen";}
		elseif 	($mgmt["STAT_INIT"] < 30)
		{$background = "yellow";}
		
		
		else
			{$background = "red";}
			
		
		echo '<td bgcolor="'. $background .'">'. $mgmt["STAT_INIT"] .'</td>';
		?>
	       
	</tr>
		<tr>
		<td>Equipment recently polled</td>
		<?php if ($mgmt["STAT_SLEEP"] > 200)
			{$background = "lightgreen";}
		elseif 	($mgmt["STAT_SLEEP"] > 100)
		{$background = "yellow";}
		
		
		else
			{$background = "red";}
			
		
		echo '<td bgcolor="'. $background .'">'. $mgmt["STAT_SLEEP"] .'</td>';
		?>
	       
	</tr>
		<tr>
		<td>Equipment ready to be polled</td>
		<?php if ($mgmt["STAT_READY"] < 10)
			{$background = "lightgreen";}
		elseif 	($mgmt["STAT_READY"] < 100)
		{$background = "yellow";}
		
		
		else
			{$background = "red";}
			
		
		echo '<td bgcolor="'. $background .'">'. $mgmt["STAT_READY"] .'</td>';
		?>
	       
	</tr>
		<tr>
		<td>Equipment in polling queue</td>
		<?php 
		$background = "lightgreen";
		
		
		
			
		
		echo '<td bgcolor="'. $background .'">'. $mgmt["STAT_INQUEUE"] .'</td>';
		?>
	       
	</tr> 
	</tr>
		<tr>
		
		<?php
		$load = sys_getloadavg();
		$t = array(1,5,15);
		$r = array(0,1,2);
		function plural($number)
		{
		 if ($number == 1)
		 {return "";}
		 else
		 {return "s";}
		 
		}
		foreach ( $r as &$i )
		{

		      if ($load[$i] < 0.60)
			     {$background = "lightgreen";}
		     elseif 	($load[$i] < 2)
		     {$background = "yellow";}
		     
		     
		     else
			     {$background = "red";}
			     
		     echo '<td>Computer Load '.$t[$i].' minute'.plural($t[$i]).'</td>';
		     echo '<td bgcolor="'. $background .'">'. $load[$i] .'</td></tr>';
		}
		?>
		

	       
	</tr>
	
 </table>
  <br />
   <table border="1" bordercolor="grey" style="background-color:lightgrey"  cellpadding="3" cellspacing="3">
	<tr>
		<td>Multiviewer Status</td></tr>
<?php 
	
	$sql = $sql = "SELECT * FROM `Multiviewer`" ;
		
		//print $sql;
		
		
            $result = query($sql);
			$num=mysqli_num_rows($result);
			//print $num;
		
	
	$i=0;
	while ($i < $num) {
		$name=mysqli_result($result,$i,"Name");
		$protocol=mysqli_result($result,$i,"Protocol");
		$status=mysqli_result($result,$i,"status");

		$ip=mysqli_result($result,$i,"IP");

		if ($status == "OK")
			$background = "lightgreen";
		elseif ($status == "STARTING")
			$background = "Yellow";
		else
			$background = "Red";
			
		echo '<tr>';
		echo '<td>'.$protocol.'</td><td><a href ="http://'. $ip . '/" target=_blank>'.$name.'</a></td>';
		echo '<td bgcolor="'. $background .'">'. $status.'</td>' ;
		
		echo '</tr>';
	
	
	$i++;
	}
	
	
		
 ?>
 </table>
   <br />
     <table border="1" bordercolor="grey" style="background-color:lightgrey"  cellpadding="3" cellspacing="3">
	<tr>
		<td>Slow IRDs</td><td>Updated</td></tr>
<?php 
	
	$sql = 'SELECT `equipment`.*,`status`.*, timestampdiff(SECOND, `status`.`updated`, now()) age
FROM equipment, status
WHERE (`status`.`updated` <= NOW() - INTERVAL 30 SECOND ) AND (`status`.`status` NOT like  "Offline") AND `equipment`.`id`= `status`.`id` ORDER BY `status`.`updated` ASC';
		
		//print $sql;
		
		
            $result = query($sql);
			$num=mysqli_num_rows($result);
			//print $num;
		
	
	$i=0;
	while ($i < $num) {
        $label=mysqli_result($result,$i,"labelnamestatic");
        $channel=mysqli_result($result,$i,"channel");
        $videoresolution=mysqli_result($result,$i,"videoresolution");
        $aspectratio=mysqli_result($result,$i,"aspectratio");
        $servicename=mysqli_result($result,$i,"servicename");
        $ip=mysqli_result($result,$i,"ip");
        $videostate=mysqli_result($result,$i,"videostate");
        $modulation=mysqli_result($result,$i,"modulationtype");
        $framerate=mysqli_result($result,$i,"framerate");
        $asioutencrypted=mysqli_result($result,$i,"asioutencrypted");
		$updated=mysqli_result($result,$i,"age");
		if ($videostate == "Running")
			$background = "lightgreen";
		else
			$background = "99FFFF";
			
		echo '<tr>';
		echo '<td bgcolor="'. $background .'"><a href ="http://'. $ip . '/" target=_blank>'. $label .'</a></td><td>'.$updated.'s</td>';
		
		echo '</tr>';
	
	
	$i++;
	}
	
	
		
 ?>
  <table border="1" bordercolor="grey" style="background-color:lightgrey"  cellpadding="3" cellspacing="3">
	<tr>
		<td>Oflline IRDs</td></tr>
<?php 
	
	$sql = 'SELECT `equipment`.*,`status`.*
FROM equipment, status
WHERE (`status`.`status` like  "Offline") AND `equipment`.`id`= `status`.`id`';
		
		//print $sql;
		
		
            $result = query($sql);
			$num=mysqli_num_rows($result);
			//print $num;
		
	
	$i=0;
	while ($i < $num) {
/*		$label=mysqli_result($result,$i,"equipment.labelnamestatic");
		$channel=mysqli_result($result,$i,"status.channel");
		$videoresolution=mysqli_result($result,$i,"status.videoresolution");
		$aspectratio=mysqli_result($result,$i,"status.aspectratio");
		$servicename=mysqli_result($result,$i,"status.servicename");
		$ip=mysqli_result($result,$i,"equipment.ip");
		$videostate=mysqli_result($result,$i,"status.videostate");
		$modulation=mysqli_result($result,$i,"status.modulationtype");
		$framerate=mysqli_result($result,$i,"status.framerate");
		$asioutencrypted=mysqli_result($result,$i,"status.asioutencrypted");*/
        $label=mysqli_result($result,$i,"labelnamestatic");
		$channel=mysqli_result($result,$i,"channel");
		$videoresolution=mysqli_result($result,$i,"videoresolution");
		$aspectratio=mysqli_result($result,$i,"aspectratio");
		$servicename=mysqli_result($result,$i,"servicename");
		$ip=mysqli_result($result,$i,"ip");
		$videostate=mysqli_result($result,$i,"videostate");
		$modulation=mysqli_result($result,$i,"modulationtype");
		$framerate=mysqli_result($result,$i,"framerate");
		$asioutencrypted=mysqli_result($result,$i,"asioutencrypted");
		if ($videostate == "Running")
			$background = "lightgreen";
		else
			$background = "99FFFF";
			
		echo '<tr>';
		echo '<td bgcolor="'. $background .'"><a href ="http://'. $ip . '/" target=_blank>'. $label .'</a></td>';
		
		echo '</tr>';
	
	
	$i++;
	}
	
	
		
 ?>
 </table>
 </body>
</html>
 