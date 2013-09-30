<html>
 <head>
 <title>
  <?php 
   $sat = $_GET['sat'];
 if ($sat == ""){
	echo "HongKongSD Receivers";
	$myFile = "HongKongSD.csv";
	$category = "HongKongSD";
} else {
	echo $sat .' Receivers';
	$myFile = $sat .".csv";
	$category = $sat;
	}
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
<td style="vertical-align:middle"> Select by category </td>
<td style="vertical-align:middle"> <form action="dummy" method="post"><select name="choice" size="1" onChange="jump(this.form)"><option value="#">Please Select</option>
<?php
$categoriesFile = "categories.csv";
$fh = fopen($categoriesFile, 'r');
	
	while ($theLine = fgets($fh) ){
	echo '<option value="ird_biss.php?sat='.$theLine.'">'.$theLine.'</option>';
	}
	fclose($fh);

	?>
</select></form></td>
</tr>
</table>

 </center>
 <?php 

	$fh = fopen($myFile, 'r');
	
	while ($theLine = fgets($fh) ){
		$split =(explode(';' , $theLine, 2));
		
		
		echo '<h3>'. $category .' '. $split[0] .'</h3><br />';
		echo '<iframe src="ird_frame.php?ip='. $split[1] .'" width="100%" height="400"></iframe>';
		echo '<br />';
	}
	
	fclose($fh);

	?>
	</body>
	</html>
