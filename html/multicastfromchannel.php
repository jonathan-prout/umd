<?php
 error_reporting(E_ALL); 
 ini_set( 'display_errors','1');
 require_once('umd.common.php');
 require_once ('sql.php');
 dbstart();
if(isset($_GET['channel']))
{
$channel = $_GET['channel'];

}else{
 $channel = "none";

}

function array_from_sql($sql_res)
{

 
 $numrows=mysql_numrows($sql_res);
  $res = array();
   $res = array_pad($res, $numrows, 0);
 //echo $numrows;
 for($x=0; $x < $numrows; $x++ )
	{
	 //echo $x;
	 
	 $row = mysql_fetch_assoc($sql_res);
	 //echo implode($row);
	  //$row = mysql_fetch_array($result, MYSQL_NUM)
	 $res[$x] =  $row;
	//}
	//$src_dest[row[0]][] = $row[1];
	
	}
	return $res;
}
//echo $channel;

  $sql = "SELECT `MulticastIp` FROM `equipment` 
            inner join `status`
            on `equipment`.`id`=`status`.`id`
             WHERE `status`.`channel` LIKE '%".$channel."%';";
  
      $sqres = mysql_query($sql);
      //echo var_dump($sqres);
      if ($sqres){
  //echo $multiviewers;
  echo json_encode(array("result"=>"OK",
                         "data"=>array_from_sql($sqres))
                   );
  }
  else{
    echo json_encode( array("result"=>"Fail")
                     );
  }



dbend();

?>