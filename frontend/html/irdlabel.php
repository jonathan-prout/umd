
 <p>Updating Labels...

 <?php
mysql_select_db("UMD") or die(mysql_error()); 

$i = 0;
$labels = $_POST['label']; 
$ids = $_POST['IRD_number']; 
$numrows =$_POST['numrows']; 
while ($i < $numrows -1) {
	$label= htmlentities($labels[$i]); 
	$id= htmlentities($ids[$i]);
	mysql_query("UPDATE equipment SET labelnamestatic = '$label' WHERE equipment.id ='$id' "); 
	#echo $id;
	#echo ', ';
	#echo $label;
	#echo '<br />';
	$i++;
	}

	echo "done <br />";
	?>