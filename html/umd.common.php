<?php
  require_once("xajax/xajax.inc.php");
  session_start();
  $xajax  = new xajax("umd.server.php");
  $xajax->registerFunction("processFormData");
?>