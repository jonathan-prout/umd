<?php
 error_reporting(E_ALL); 
 ini_set( 'display_errors','1');

 //var_dump($_POST);
 
$sql = 'SELECT `customlabel`.*'
 . ' FROM customlabel'
 . ' ORDER BY `customlabel`.`id` ASC';  
     //print $sql;
		 
				 
$result = mysql_query($sql);
$num=mysql_numrows($result);

for ($i = 0; $i < $num; $i++) {
		 
		$id=mysql_result($result,$i,"id");
		$top=$_POST['top'.$id];
		
		$bottom=$_POST['bottom'.$id];
		$sameas=$_POST['select'.$id];
		if($sameas != "-1"){
		 mysql_query("UPDATE customlabel SET top = 'sameas=$sameas' WHERE customlabel.id ='$id' ");
		}
		else{
		 mysql_query("UPDATE customlabel SET top = '$top' WHERE customlabel.id ='$id' ");
		mysql_query("UPDATE customlabel SET bottom = '$bottom' WHERE customlabel.id ='$id' ");
		}
		
 		
		

}

 ?>
 



 <p>Updating Labels...</p>

 

