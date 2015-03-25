<?php
 // Remove unnecessary errors
 //error_reporting(E_ALL);
 // Report simple running errors
 error_reporting(E_ERROR | E_WARNING | E_PARSE);
 ini_set( 'display_errors','1');
 require_once('umd.common.php');
 require_once ('sql.php');
 dbstart();

?>
<html>
 <head>
 <title>
  <?php
  
  if (array_key_exists( 'mv' , $_POST ))
 $mv = $_POST['mv'];
else
 $mv = "";
 if ($mv == "")
	echo "UMD Labels for all multiviewers";
else
	echo 'UMD Labels for '.$mv
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
formused="table";
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
if ($_SERVER['REQUEST_METHOD'] != 'POST'){
	if ($mv == "")
	include("login.php");
	else
	{
	
	include("table.php");
	}
}
else
{
	if ($_POST['formused'] == "table")
	{
		include("process.php");
		include("table.php");
	}
	else
	{
		if (($_POST['username'] == "evc") && ($_POST['password'] == "evcpass"))
		{
			include("table.php");
		}
		else
		{
		echo "Wrong username or password!!";
		include("login.php");
		}
	}
}	
?>	
	

	


</html>
