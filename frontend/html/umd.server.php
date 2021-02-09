<?php
   require_once("umd.common.php");
   require_once("sql.php");
 
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






?>