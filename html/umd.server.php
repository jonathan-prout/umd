<?php
   require_once("umd.common.php");
   require_once("config.inc.php");
 
function processFormData($aFormValues,$id,$kaleidoIP)
{
   // if (array_key_exists("site_id",$aFormValues))
   // {
    	if ($id == "submitButton"){
    		return updateDB($aFormValues,$kaleidoIP);
    	}
    //	else if ($id =="submitButtonAdd"){
    //		return addDataToDB($aFormValues);
    //    }
    //    else{
    //     	 return collapse();
    //     }
    //}
	 
}




function updateDB($aFormValues,$kaleidoIP)
{
	$objResponse = new xajaxResponse();
	dbstart();
	
	
	$label1 = $aFormValues['label1'];
	$label2 = $aFormValues['label2'];
	$label3 = $aFormValues['label3'];
	$label4 = $aFormValues['label4'];
	$label5 = $aFormValues['label5'];
	$label6 = $aFormValues['label6'];
	$label7 = $aFormValues['label7'];
	$label8 = $aFormValues['label8'];
	$label9 = $aFormValues['label9'];
	$label10 = $aFormValues['label10'];
	$label11 = $aFormValues['label11'];
	$label12 = $aFormValues['label12'];
	$label13 = $aFormValues['label13'];
	$label14 = $aFormValues['label14'];
	$label15 = $aFormValues['label15'];
	$label16 = $aFormValues['label16'];
	$label17 = $aFormValues['label17'];
	$label18 = $aFormValues['label18'];
	
	$sql    = "UPDATE equipment SET labelnamestatic = '$label1' WHERE equipment.kid ='1' AND kaleidoaddr = '$kaleidoIP' ";
	$sql1   = "UPDATE equipment SET labelnamestatic = '$label2' WHERE equipment.kid ='2'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql2   = "UPDATE equipment SET labelnamestatic = '$label3' WHERE equipment.kid ='3'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql3   = "UPDATE equipment SET labelnamestatic = '$label4' WHERE equipment.kid ='4' AND kaleidoaddr = '$kaleidoIP'  ";
	$sql4   = "UPDATE equipment SET labelnamestatic = '$label5' WHERE equipment.kid ='5' AND kaleidoaddr = '$kaleidoIP' ";
	$sql5   = "UPDATE equipment SET labelnamestatic = '$label6' WHERE equipment.kid ='6'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql6   = "UPDATE equipment SET labelnamestatic = '$label7' WHERE equipment.kid ='7' AND kaleidoaddr = '$kaleidoIP' ";
	$sql7   = "UPDATE equipment SET labelnamestatic = '$label8' WHERE equipment.kid ='8'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql8   = "UPDATE equipment SET labelnamestatic = '$label9' WHERE equipment.kid ='9'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql9   = "UPDATE equipment SET labelnamestatic = '$label10' WHERE equipment.kid ='10'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql10  = "UPDATE equipment SET labelnamestatic = '$label11' WHERE equipment.kid ='11'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql11  = "UPDATE equipment SET labelnamestatic = '$label12' WHERE equipment.kid ='12'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql12  = "UPDATE equipment SET labelnamestatic = '$label13' WHERE equipment.kid ='13'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql13  = "UPDATE equipment SET labelnamestatic = '$label14' WHERE equipment.kid ='14'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql14  = "UPDATE equipment SET labelnamestatic = '$label15' WHERE equipment.kid ='15'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql15  = "UPDATE equipment SET labelnamestatic = '$label16' WHERE equipment.kid ='16'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql16  = "UPDATE equipment SET labelnamestatic = '$label17' WHERE equipment.kid ='17'  AND kaleidoaddr = '$kaleidoIP' ";
	$sql17  = "UPDATE equipment SET labelnamestatic = '$label18' WHERE equipment.kid ='18'  AND kaleidoaddr = '$kaleidoIP' ";
	
	
	
	if (strlen($label1) > 0) {$result = mysql_query($sql); }
	if (strlen($label2) > 0)  { $result = mysql_query($sql1);}
	if (strlen($label3) > 0)  { $result = mysql_query($sql2);}
	if (strlen($label4) > 0)  { $result = mysql_query($sql3);}
	
	if (strlen($label5) > 0)  { $result = mysql_query($sql4);}
	if (strlen($label6) > 0)  { $result = mysql_query($sql5);}
	if (strlen($label7) > 0)  { $result = mysql_query($sql6);}
	if (strlen($label8) > 0)  { $result = mysql_query($sql7);}
	if (strlen($label9) > 0)  { $result = mysql_query($sql8);}
	if (strlen($label10) > 0)  { $result = mysql_query($sql9);}
	if (strlen($label11) > 0)  { $result = mysql_query($sql10);}
	if (strlen($label12) > 0)  { $result = mysql_query($sql11);}
	if (strlen($label13) > 0)  { $result = mysql_query($sql12);}
	if (strlen($label14) > 0)  { $result = mysql_query($sql13);}
	if (strlen($label15) > 0)  { $result = mysql_query($sql14);}
	if (strlen($label16) > 0)  { $result = mysql_query($sql15);}
	if (strlen($label17) > 0)  { $result = mysql_query($sql16);}
	if (strlen($label18) > 0)  { $result = mysql_query($sql17);}

 
  $nForm = "<form>";
 	$nForm .= "<BR />";
 	$nForm .= $sql;
 	$nForm .= $label1;		
  $nForm .= $label2; 	
 	$nForm .= $label3;		
  $nForm .= $label4; 	
 	$nForm .= $label5;		
  $nForm .= $label6; 	
 	$nForm .= $label7;		
  $nForm .= $label8; 	
 	$nForm .= $label9;		
  $nForm .= $label10; 	
 	$nForm .= $label11;		
  $nForm .= $label12; 	
 	$nForm .= $label13;		
  $nForm .= $label14; 	
 	$nForm .= $label15;		
  $nForm .= $label16; 	
 	$nForm .= $label17;		
  $nForm .= $label18;
  
   	
 
  $nForm .= " <!-- <BR /><input type=\"submit\" name=\"delete\" value=\"Done\"></form> -->DONE";
        
	$objResponse->addAssign("outputDiv","innerHTML",$nForm);
	
	
	return $objResponse;	
}

$xajax->processRequests();


?>