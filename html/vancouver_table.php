<?php
 error_reporting(E_ALL); 
 ini_set( 'display_errors','1');
?>

 <form method="post" action="<?php echo $_SERVER['PHP_SELF'];?>">
<input type="hidden" name="formused" value="table">

<h3>Eurovision UMD Manager: Custom Labels</h3>                
<table width="" height="*" border="1" cellpadding="1">
  <tr>
    <td><table width="600" height="" border="1" cellpadding="1">
      <tr>

          
     <?
            $sql = 'SELECT `customlabel`.*, `Multiviewer`.`Name`
FROM customlabel, Multiviewer
WHERE (`Multiviewer`.`IP` =`customlabel`.`kaleidoaddr`)';  
            //print $sql;
			
					
            $result = mysql_query($sql);
			$num=mysql_numrows($result);
			//print $num;
			//print $result;
	$sql = 'SELECT `id`,`labelnamestatic` FROM `equipment` WHERE 1';
	$irds = mysql_query($sql);
	$numirds=mysql_numrows($irds);
	$i=0;
	$j=1;
	while ($i < $num) {
			
		$id=mysql_result($result,$i,"customlabel.id");
		$kaladdr=mysql_result($result,$i,"customlabel.kaleidoaddr");
		$top=mysql_result($result,$i,"customlabel.top");
		$bottom=mysql_result($result,$i,"customlabel.bottom");
		$input=mysql_result($result,$i,"customlabel.input");
		$name=mysql_result($result,$i,"Multiviewer.Name");
		
			
			
			
		
		echo '<td><label>';
        echo 'Multiviewer '. $name.', Input '.$input;
		echo '<br />';
		?>
        TOP<input type="text" name="<? echo 'top'.$id; ?>" id="<? echo 'top'.$id; ?>" value="<? echo $top; ?>" />BOTTOM<input type="text" name="<? echo 'bottom'.$id; ?>" id="<? echo 'bottom'.$id; ?>" value="<? echo $bottom; ?>" /><select name="<? echo 'select'.$id; ?>">
	<option value="-1">Use Label for...</option>
	<? for($x=0; $x < $numirds; $x++ ){
	  $rxid=mysql_result($irds,$x,"id");
	  $labelnamestatic=mysql_result($irds,$x,"labelnamestatic");
	  echo '<option value="'.$rxid.'">'.$labelnamestatic.'</option>';
	} ?>
	</select>
        <?  echo '</label></td>';
	  
			echo '</tr>';
			
			
		
		$i++;
		$j++;
	}
	
	if ($j != 1)
		echo '</tr>';
		
	?>
</table>
			

<input type="submit" value="Submit"> 


           </form>
        </div>
     
     
     </div>
     
     <div id="outputDiv">
     	
     </div>

 </body>