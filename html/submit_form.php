
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
 }
 else
 {
    echo "form name ".$POST["formName"]. " not implimented";
 }
 
 
 dbend();

}else //no post
{
    echo "ERROR: This page should be accessed via POST.";
}
?>
