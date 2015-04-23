
<?php
 error_reporting(E_ALL); 
 ini_set( 'display_errors','1');
 ?>
 <?php
 
//echo $_SERVER['REQUEST_METHOD'];
if ($_SERVER['REQUEST_METHOD']=="POST"){ 

$echo_out = 0;
if($echo_out){

    foreach ($_POST as $key => $value) {

        echo $key;
        echo "-";
        echo $value;
        echo "\n";
    }
}
 require_once('umd.common.php');
 require_once ('sql.php');
 dbstart();
if (isset($_POST['formName'])) {
if ($_POST["formName"] == "updateMVInput"){
  if ($_POST["inputStrategy"] == "Null"){  
    echo "Input Strategy must be set";
  }else{
    $sql = "UPDATE `UMD`.`mv_input` SET";
    //$sql = $sql." `multiviewer` = '".$_POST["multiviewerID"]."',";
    //$sql = $sql." `input` = '".$_POST["mvIn"]."',";
    $sql = $sql." `strategy` = '".$_POST["inputStrategy"]."',";
   
    if ($_POST["equipment"] == "Null"){
        $sql = $sql." `equipment` = NULL,";
    }else
    {
        $sql = $sql." `equipment` = '".$_POST["equipment"]."',";
    }
     if ($_POST["mtx_out_sdi"] == "null"){
        $sql = $sql." `inputmtxname` = NULL,";
    }else
    {
            
        
        $ressource = mysql_select_db("matrix");
        
        $mtx_out = mysql_query('SELECT `name` FROM `output` WHERE `PRIMARY` ="'.$_POST["mtx_out_sdi"].'";');
        //echo('SELECT `name` FROM `output` WHERE `PRIMARY` ="'.$_POST["mtx_out"].'";');
        $ressource = mysql_select_db("umd");
        $numrows=mysql_numrows($mtx_out);
        //echo mysql_result($mtx_out,0,"name");
        if($numrows == 0){
            
            $sql = $sql." `inputmtxname` = NULL,";
        }else{
            $sql = $sql." `inputmtxname` = '".mysql_result($mtx_out,0,"name")."',";
        }
    
        
         
    }
   
    if ($_POST["customlabel1"] == "null"){
        $sql = $sql." `customlabel1` = NULL,";
    }else
    {
        $sql = $sql." `customlabel1` = '".$_POST["customlabel1"]."',";
    }
    if ($_POST["customlabel2"] == "null"){
        $sql = $sql." `customlabel2` = NULL";
    }else
    {
        $sql = $sql." `customlabel2` = '".$_POST["customlabel2"]."'";
    }
    
    $sql = $sql." WHERE `mv_input`.`PRIMARY` =".$_POST["PRIMARY"].";";
		
	//echo $sql;
//		
           $result = mysql_query($sql);
           if($result == TRUE){
            echo "OK";
           }else{
            echo "ERROR: Database problem with '".$sql."'";
           }
        
             }
 }
 elseif($_POST["formName"] == "updateIRD")
 {
    //formName=updateIRD
    //equipmentID=219
    //name=HGKG+11
    //ip=10.75.15.98
    //labelnamestatic=11+HGKG
    //MulticastIp=null
    //InMTXName=4
    //OutMTXName=2
    //SAT1=AS
    //SAT2=Null
    //SAT3=Null
    //SAT4=Null
    //doesNotUseGateway=on
    //Demod=251
    //Isdemod=on
    //{"id":"252","model_id":"NS2000_SNMP","ip":"10.75.15.115","name":"DEM 20 HGKG",
    //"labelnamestatic":"DEM 20 HGKG","MulticastIp":null,"InMTXName":null,"OutMTXName":null,
    //"SAT1":"AS","SAT2":"","SAT3":"","SAT4":"","doesNotUseGateway":"0","lo_offset":"0","Demod":"0","Isdemod":"1"}
    
    $sql = "UPDATE `UMD`.`equipment` SET ";
    $search = array("\n", "\r", "\u", "\\t", "\t", "\f", "\b", "/", '\\',  ";", "null");
    $replace = array("", "", "", "", "","", "", "", "", "", "");
    $keys = array("Demod", "MulticastIp");
    $args = array();
    foreach($keys as $key){
        if($_POST[$key] == "null")
        {
            $args[] =" `$key` = NULL";
        }else
        {
            $args[] =" `$key` = '".str_replace($search, $replace,$_POST[$key])."'";
        }
       
    }
    
    $ressource = mysql_select_db("matrix");
        
    $InMTXName = mysql_query('SELECT `name` FROM `output` WHERE `PRIMARY` ="'.$_POST["InMTXName"].'";');
    $OutMTXName = mysql_query('SELECT `name` FROM `input` WHERE `PRIMARY` ="'.$_POST["OutMTXName"].'";');
    //echo('SELECT `name` FROM `output` WHERE `PRIMARY` ="'.$_POST["mtx_out"].'";');
    $ressource = mysql_select_db("umd");
    $numrows=mysql_numrows($InMTXName);
        //echo mysql_result($mtx_out,0,"name");
        if($numrows == 0){
            
            $sql = $sql." `InMTXName` = NULL,";
        }else{
            $sql = $sql." `InMTXName` = '".mysql_result($InMTXName,0,"name")."',";
        }
    $numrows=mysql_numrows($OutMTXName);
        //echo mysql_result($mtx_out,0,"name");
        if($numrows == 0){
            
            $sql = $sql." `OutMTXName` = NULL,";
        }else{
            $sql = $sql." `OutMTXName` = '".mysql_result($OutMTXName,0,"name")."',";
        }
    $keys = array("name", "ip", "labelnamestatic", "SAT1", "SAT2", "SAT3", "SAT4");
    foreach($keys as $key){
       $args[] =" `$key` = '".str_replace($search, $replace,$_POST[$key])."'"; 
    }
    $checkboxes = array("doesNotUseGateway", "Isdemod");
    foreach($checkboxes as $cb){
        //echo "Foo";
        $v = (!empty($_POST[$cb]));
        echo $v;
        if ($v){
           $args[] =" `$cb` = 1";
            
        }else {
           
            $args[] =" `$cb` = 0"; 
        
        }
    }
    $sql = $sql.join(",", $args)." WHERE `equipment`.`id` =".$_POST["equipmentID"].";";
    //echo $sql;
    $result = mysql_query($sql);
          if($result == TRUE){
           echo "OK";
          }else{
          echo "ERROR: Database problem with '".$sql."'";
           }
 } elseif($_POST["formName"] == "addMV"){
    $err = FALSE;
    $errCause = "I'm not going to tell you";
    
    if (isset($_POST['name'])) {
        $name = strip_tags($_POST['name']);
    }else{
        $err = True;
        $errCause = "You didn't give the Multiviewer a name";
    }
    if (isset($_POST['ip'])) {
        $ip = strip_tags($_POST['ip']);
        $result = mysql_query("SELECT * FROM `Multiviewer` WHERE `IP` LIKE '".$ip."'");
        $numrows=mysql_numrows($result);
        if($numrows > 0){
                    $err = True;
                    $errCause = "IP Address is not unique";
        }
    }else{
        $err = True;
        $errCause = "You didn't give the Multiviewer an address";
    }
    if ($_POST['protocolSelect'] != "null") {
        $protocol = strip_tags($_POST['protocolSelect']);
    }else{
        $err = True;
        $errCause = "You didn't give the Multiviewer a protocol";
    }
    if (intval($_POST['numInputs']) != 0) {
        $numInputs = intval(strip_tags($_POST['numInputs']));
    }else{
        $err = True;
        $errCause = "You didn't give the Multiviewer any inputs. Supplied value ".intval($_POST['numInputs']);
    }
    if ($err == False){
        $sql = 'INSERT INTO `UMD`.`Multiviewer` (`id` ,`Name` ,`IP` ,`Protocol` ,`status`) ';
        $sql = $sql.' VALUES (NULL , "'.$name.'", "'.$ip.'", "'.$protocol.'", "New");';
        //echo $sql;
        $result = mysql_query($sql);
        if(mysql_error())
        {
            die(mysql_ederror());
            }
        $newMV = mysql_insert_id();
        for ($i = 1; $i <= $numInputs; $i++) {
            $sql = 'INSERT INTO `UMD`.`mv_input` (`PRIMARY` ,`multiviewer` ,`input` ,`labeladdr1` ,`labeladdr2` ,`strategy` ,`equipment` ,`inputmtxid` ,`inputmtxname` ,`customlabel1` ,`customlabel2`)';
            $sql = $sql.' VALUES (NULL , "'.$newMV.'", "'.$i.'", NULL , NULL , "4", NULL , NULL , NULL , "'.$name.' Input '.$i.'", NULL);';
            $result = mysql_query($sql);
            if(mysql_error())
        {
            die(mysql_error());
            }
        } 
        echo '<br><br><span class="alert alert-success">';
        echo '<a href="#" class="close" data-dismiss="alert">&times;</a>';
        echo '<strong>Multiviewer added OK.</strong><br>';
        echo '</span><br><br>';
    }else{
        echo '<br><br><span class="alert alert-error">';

        echo '<a href="#" class="close" data-dismiss="alert">&times;</a>';

        echo '<strong>Error!</strong> A problem has been occurred while submitting your data. Because '.$errCause.'<br>';

        echo '</span><br><br>';


    }
    


 
}elseif($_POST["formName"] == "newIRD")
 {
    //formName=updateIRD
    //equipmentID=219
    //name=HGKG+11
    //ip=10.75.15.98
    //labelnamestatic=11+HGKG
    //MulticastIp=null
    //InMTXName=4
    //OutMTXName=2
    //SAT1=AS
    //SAT2=Null
    //SAT3=Null
    //SAT4=Null
    //doesNotUseGateway=on
    //Demod=251
    //Isdemod=on
    //{"id":"252","model_id":"NS2000_SNMP","ip":"10.75.15.115","name":"DEM 20 HGKG",
    //"labelnamestatic":"DEM 20 HGKG","MulticastIp":null,"InMTXName":null,"OutMTXName":null,
    //"SAT1":"AS","SAT2":"","SAT3":"","SAT4":"","doesNotUseGateway":"0","lo_offset":"0","Demod":"0","Isdemod":"1"}
    
    //    INSERT INTO `UMD`.`equipment` (
    //`id` ,
    //`model_id` ,
    //`ip` ,
    //`name` ,
    //`labelnamestatic` ,
    //`MulticastIp` ,
    //`InMTXName` ,
    //`OutMTXName` ,
    //`SAT1` ,
    //`SAT2` ,
    //`SAT3` ,
    //`SAT4` ,
    //`doesNotUseGateway` ,
    //`lo_offset` ,
    //`Demod` ,
    //`Isdemod`
    //)
    //VALUES (
    //NULL , '1', '', '', '', NULL , NULL , NULL , '', '', '', '', '0', '0', '0', '0'
    //);
    $sql = "INSERT INTO `UMD`.`equipment` ( `id`, ";
    $search = array("\n", "\r", "\u", "\\t", "\t", "\f", "\b", "/", '\\',  ";", "null");
    $replace = array("", "", "", "", "","", "", "", "", "", "");
    $keys = array("Demod", "MulticastIp");
    $args = array();
    foreach($keys as $key){
        if($_POST[$key] == "null")
        {
            $args[] ="NULL";
        }else
        {
            $args[] ="'".str_replace($search, $replace,$_POST[$key])."'";
        }
       
    }
    
    
    $keys2 = array("name", "ip", "labelnamestatic", "SAT1", "SAT2", "SAT3", "SAT4", "model_id");
    foreach($keys2 as $key){
       $args[] ="'".str_replace($search, $replace,$_POST[$key])."'"; 
    }
    $checkboxes = array("doesNotUseGateway", "Isdemod");
    foreach($checkboxes as $cb){
        //echo "Foo";
        $v = (!empty($_POST[$cb]));
        echo $v;
        if ($v){
           $args[] ="1";
            
        }else {
           
            $args[] ="0"; 
        
        }
    }
    $ressource = mysql_select_db("matrix");
        
    $InMTXName = mysql_query('SELECT `name` FROM `output` WHERE `PRIMARY` ="'.$_POST["InMTXName"].'";');
    $OutMTXName = mysql_query('SELECT `name` FROM `input` WHERE `PRIMARY` ="'.$_POST["OutMTXName"].'";');
    //echo('SELECT `name` FROM `output` WHERE `PRIMARY` ="'.$_POST["mtx_out"].'";');
    $ressource = mysql_select_db("umd");
    $numrows=mysql_numrows($InMTXName);
        //echo mysql_result($mtx_out,0,"name");
        if($numrows == 0){
            
            $args[] ="NULL";
        }else{
            $args[] = "'".mysql_result($InMTXName,0,"name")."'";
        }
    $numrows=mysql_numrows($OutMTXName);
        //echo mysql_result($mtx_out,0,"name");
        if($numrows == 0){
            
            $args[] ="NULL";
        }else{
            $args[] = "'".mysql_result($OutMTXName,0,"name")."'";
        }
        
    
    $sql = $sql.join(", ", $keys).",".join(", ", $keys2).",".join(", ", $checkboxes).",  InMTXName, OutMTXName) VALUES ( NULL, ".join(",", $args).");";
    //echo $sql;
    $result = mysql_query($sql);
          if($result == TRUE){
           echo '<br><br><span class="alert alert-success">';
        echo '<a href="#" class="close" data-dismiss="alert">&times;</a>';
        echo '<strong>Equipment added OK.</strong><br>';
        echo '</span><br><br>';
    }else{
        if(mysql_error())
        {
            $errCause =mysql_error();
            
        } else {
            $errCause = "Unknown Error";
        }
        echo '<br><br>span class="alert alert-error">';

        echo '<a href="#" class="close" data-dismiss="alert">&times;</a>';

        echo '<strong>Error!</strong> A problem has been occurred while submitting your data. Because '.$errCause.'<br>';

        echo '</span><br><br>';
    }
 }
 else
 {
    echo "form name ".$_POST["formName"]. " not implimented";
 }
}
 else
 {
    echo "form name  not supplied";
       foreach ($_POST as $key => $value) {

        echo $key;
        echo "-";
        echo $value;
        echo "\n";
    }
 } 
 
 dbend();

}else //no post
{
    echo "ERROR: This page should be accessed via POST.";
}
?>
