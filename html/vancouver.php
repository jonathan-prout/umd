<?php

 require_once('umd.common.php');
 require_once ('config.inc.php');
 dbstart();

?>
<html>
 <head>

 </head>
 <body>
<?php
if ($_SERVER['REQUEST_METHOD'] != 'POST'){
	include("vancouver_login.php");
}
else
{
	if ($_POST['formused'] == "table")
	{
		include("process2.php");
		include("vancouver_table.php");
	}
	else
	{
		if (($_POST['username'] == "evc") && ($_POST['password'] == "evcpass"))
		{
			include("vancouver_table.php");
		}
		else
		{
		echo "Wrong username or password!!";
		include("vancouver_login.php");
		}
	}
}	
?>	
	

	

 </body>
</html>
