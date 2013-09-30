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
 
 <?php 
	$myFile = "testFile.txt";
	$fh = fopen($myFile, 'r');
	
	while ($theLine = fgets($fh) ){
		$split =(explode(';' , $theLine, 2));
		
		
		echo '<h3>'. $split[0] .'</h3><br />';
		echo '<iframe src="http://'. $split[1] .'/tcf?cgi=show&$path=/Conditional Access" width="100%" height="300"></iframe>';
		echo '<br />';
	}
	
	fclose($fh);

	?>
	</body>
	</html>
