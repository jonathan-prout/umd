<?php
 //usage: http://fxchange1.ebu.ch/umd/umd.php?id=1
 //id = 1 equivalent a 192.168.58.1
 //$kaleidoconv = array(1 => "192.168.3.51",
 //                     2 => "192.168.3.52",
 //                     3 => "192.168.3.53",
 //                     4 => "192.168.3.54",
 //                     5 => "192.168.3.55",
 //                     6 => "192.168.3.56",
 //                     7 => "192.168.3.57",
 //                     8 => "192.168.3.58",
 //                     9 => "192.168.3.59");    
 //
 require_once('umd.common.php');
 require_once ('sql.php');
 dbstart();
 $kaleido = $_GET['id'];
 $kip = $kaleidoconv[$kaleido];
?>
<html>
 <head>
 <?php $xajax->printJavascript('xajax/'); ?>
    <script type="text/javascript">
       function submitUMD(){    
            xajax_processFormData(xajax.getFormValues('updateUMD'),'submitButton','<? print $kip; ?>');
         return false;
       }
    </script>
 </head>
 <body>
 	<? print $kaleido; ?>
     <div id="formEquipment">
        <div id="formDiv">
        
           <form id="updateUMD" action="javascript:void(null);"  >


  
                     
<table width="800" height="398" border="1" cellpadding="1">
  <tr>
    <td><table width="400" height="382" border="1" cellpadding="1">
      <tr>
        <td>
          <label>
         <?
            $sql = "SELECT kid,labelnamestatic FROM equipment WHERE kaleidoaddr = '$kip' ORDER BY equipment.id ASC";
            //print $sql;
            $result = mysql_query($sql);
            while($row = mysql_fetch_array($result)){
            	    $id = $row["kid"];
            	    $label = $row["labelnamestatic"];
            	    if ($id == 1) { $nlabel1 = $label; }
            	    if ($id == 2) { $nlabel2 = $label; }
            	    if ($id == 3) { $nlabel3 = $label; }
            	    if ($id == 4) { $nlabel4 = $label; }
            	    if ($id == 5) { $nlabel5 = $label; }
            	    if ($id == 6) { $nlabel6 = $label; }
            	    if ($id == 7) { $nlabel7 = $label; }
            	    if ($id == 8) { $nlabel8 = $label; }
            	    if ($id == 9) { $nlabel9 = $label; }
            	    if ($id == 10) { $nlabel10 = $label; }
            	    if ($id == 11) { $nlabel11 = $label; }
            	    if ($id == 12) { $nlabel12 = $label; }
            	    if ($id == 13) { $nlabel13 = $label; }
            	    if ($id == 14) { $nlabel14 = $label; }
            	    if ($id == 15) { $nlabel15 = $label; }
            	    if ($id == 16) { $nlabel16 = $label; }
            	    if ($id == 17) { $nlabel17 = $label; }
            	    if ($id == 18) { $nlabel18 = $label; }            	                	                	                	              
           }
      
         ?>
          1
          <input type="text" name="label1" id="1" value="<? echo $nlabel1; ?>" />
          </label></td>
        <td><label>
        	2
          <input type="text" name="label2" id="12" value="<? echo $nlabel2; ?>" />
        </label></td>
        <td><label>
        	3
          <input type="text" name="label3" id="13" value="<? echo $nlabel3; ?>" />
        </label></td>
      </tr>
      <tr>
        <td><label>7
          <input type="text" name="label7" id="14" value="<? echo $nlabel7; ?>" />
        </label></td>
        <td><label>8
          <input type="text" name="label8" id="15" value="<? echo $nlabel8; ?>"/>
        </label></td>
        <td><label>9
          <input type="text" name="label9" id="16" value="<? echo $nlabel9; ?>" />
        </label></td>
      </tr>
      <tr>
        <td><label>13
          <input type="text" name="label13" id="17" value="<? echo $nlabel13; ?>" />
        </label></td>
        <td><label>14
          <input type="text" name="label14" id="18" value="<? echo $nlabel14; ?>" />
        </label></td>
       <!-- <td><label>15  <input type="text" name="label15" id="19" value="<? echo $nlabel15; ?>" />
        </label>
        </td> -->
        <td> </td>
        
      </tr>
    </table></td>
    <td><table width="400" height="378" border="1" cellpadding="1">
      <tr>
        <td>4<input type="text" name="label4" id="110" value="<? echo $nlabel4; ?>" /></td>
        <td>5<input type="text" name="label5" id="111" value="<? echo $nlabel5;; ?>" /></td>
        <td>6<input type="text" name="label6" id="112" value="<? echo $nlabel6; ?>" /></td>
      </tr>
      <tr>
        <td>10<input type="text" name="label10" id="113" value="<? echo $nlabel10; ?>" /></td>
        <td>11<input type="text" name="label11" id="114" value="<? echo $nlabel11; ?>" /></td>
        <td>12<input type="text" name="label12" id="115" value="<? echo $nlabel12; ?>" /></td>
      </tr>
      <tr>
      
       <td> </td>
      <td><label>15  <input type="text" name="label15" id="19" value="<? echo $nlabel15; ?>" />
        </label>
        </td>
        
        <td>16<input type="text" name="label16" id="118" value="<? echo $nlabel16; ?>" /></td>
        
          
       <!-- <td>17<input type="text" name="label17" id="117" value="<? echo $nlabel17; ?>" /></td>
        <td>18<input type="text" name="label18" id="116" value="<? echo $nlabel18; ?>" /></td>
        -->
  
      </tr>
    </table></td>
  </tr>
</table>

 
        
             <table>
             <tr>
             <td>
             <div class="submitDiv"> 
                 <input id="submitButton" type="submit" value="Update Kaleido Label!" onClick="submitUMD();" />
             </div>
             </td> 
             </tr>
             </table>
           </form>
        </div>
     
     
     </div>
     
     <div id="outputDiv">
     	
     </div>

 </body>
</html>
