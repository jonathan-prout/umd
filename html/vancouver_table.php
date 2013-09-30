 <form method="post" action="<?php echo $PHP_SELF;?>">
<input type="hidden" name="formused" value="table">

                     
<table width="" height="*" border="1" cellpadding="1">
  <tr>
    <td><table width="400" height="382" border="1" cellpadding="1">
      <tr>

          
     <?
            $sql = 'SELECT `customlabel`.*'
        . ' FROM customlabel'
        . ' ORDER BY `customlabel`.`id` ASC';  
            //print $sql;
			
					
            $result = mysql_query($sql);
			$num=mysql_numrows($result);
			//print $num;
			//print $result;
	
	$i=0;
	$j=1;
	while ($i < $num) {
			
		$id=mysql_result($result,$i,"id");
		$name=mysql_result($result,$i,"name");
		$labeladdr=mysql_result($result,$i,"labeladdr");
		$text=mysql_result($result,$i,"text");
		
			
			
			
		
		echo '<td><label>';
        echo $name;
		echo '<br />';
		?>
        <input type="text" name="label<? echo $id; ?>" id="<? echo $id; ?>" value="<? echo $text; ?>" />
        <?  echo '</label></td>';
		if  ($j == 4){
			echo '</tr>';
			$j = 0;
			}
		
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

