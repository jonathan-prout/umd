<html>
 <head>
 <title>
  <?php 
   $sat = $_GET['sat'];
   $svc = $_GET['svc'];
 if ($sat == ""){
	$myFile = "805Mux.csv";
	$category = "805Mux";
} else {
	
	$myFile = $sat .".csv";
	$category = $sat;
	}
	echo $category .' Encoders';

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
 <table border="0"width="50%">
<tr>	
<td style="vertical-align:middle"> Select category </td>
<td style="vertical-align:middle"> <form action="dummy" method="post"><select name="choice" size="1" onChange="jump(this.form)"><option value="#">Please Select</option>
<?php
$categoriesFile = "categories_encoder.csv";
$fh = fopen($categoriesFile, 'r');
	
	while ($theLine = fgets($fh) ){
	echo '<option value="encoder_quick.php?sat='.$theLine.'">'.$theLine.'</option>';
	}
	fclose($fh);

	?>
</select></form></td>
</tr>
</table>
<hr />

 <?php 
	echo '<a href="encoder_quick.php?svc=ALL&sat='. $sat.'"><h3>All Encoders</h3></a><br /> ';
	$fh = fopen($myFile, 'r');
	
	while ($theLine = fgets($fh) ){
		$split =(explode(';' , $theLine, 3));
		$type = $split[2];
		
		if (strlen(strstr($type,"E5710"))>0) {
		$type = "E5710";
		}
		if (strlen(strstr($type,"E5782"))>0) {
		$type = "E5782";
		}
		$expand = FALSE;
		if ($svc == $split[0] )
			$expand = TRUE;
		if($svc == "ALL")
			$expand = TRUE;

		if($expand == TRUE)
		{
			
			if ($type == "E5710")
			{
				echo '<h3>'. $category .' '. $split[0] .'</h3><br />';
				echo '<table border="0" width="1050">';
				echo '<tr>';
				echo "\n";
				echo '<td style="vertical-align:middle" width ="220">';
				echo '<iframe src="http://'. $split[1] .'/local?Cid.4=frame" width="220" height="300" scrolling="no"></iframe><br />';
				echo '<iframe src="http://'. $split[1] .'/local?Cid.3=frame" width="220" height="140" scrolling="no"></iframe><br />';
				echo '<iframe src="http://'. $split[1] .'/local?Cid.5=frame" width="220" height="60" scrolling="no"></iframe>';
				echo ' </td>';
				echo "\n";
				echo '<td style="vertical-align:middle" width ="400">';
				echo '<iframe src="http://'. $split[1] .'/local?path=Mux" width="400" height="500"></iframe>';
				echo ' </td>';
				echo "\n";
				echo '<td style="vertical-align:middle" width ="400">';
				echo '<iframe src="http://'. $split[1] .'/local?path=SD Video Module+" width="400" height="500"></iframe>';
				echo ' </td>';
				echo "\n";
				echo ' </tr></table><br />';
				echo "\n";
			} elseif($type == "E5782")
			{
				echo '<h3>'. $category .' '. $split[0] .'</h3><br /> ';
				echo '<table border="0" width="1050">';
				echo '<tr>';
				echo "\n";
				echo '<td style="vertical-align:middle" width ="220">';
				echo '<iframe src="http://'. $split[1] .'/local?Cid.4=frame" width="220" height="300" scrolling="no"></iframe><br />';
				echo '<iframe src="http://'. $split[1] .'/local?Cid.3=frame" width="220" height="140" scrolling="no"></iframe><br />';
				echo '<iframe src="http://'. $split[1] .'/local?Cid.5=frame" width="220" height="60" scrolling="no"></iframe>';
				echo ' </td>';
				echo "\n";
				echo '<td swidth ="400">';
				echo '<iframe src="http://'. $split[1] .'/local?path=Mux" width="400" height="500"></iframe>';
				echo ' </td>';
				echo "\n";
				echo '<td width ="400">';
				echo '<iframe src="http://'. $split[1] .'/local?path=Video Source+" width="400" height="500"></iframe>';
				echo ' </td>';
				echo "\n";
				echo ' </tr></table><br />';
				echo "\n";
			}
			else
			echo $type;
		}
		else {
		echo '<a href="encoder_quick.php?svc='.$split[0].'&sat='. $sat.'"><h3>'. $category .' '. $split[0] .'</h3></a><br /> ';
		}
		
	}
	
	fclose($fh);

	?>
	</body>
	</html>
