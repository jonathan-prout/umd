<html>
 <head>
</head>
<frameset rows="*,90">
  <?php 
   $ip = $_GET['ip']; ?>

<frame name="mainFrame" src="http://<?php echo $ip ?>/tcf?cgi=show&$path=/Conditional Access" frameborder="0" border="0">
<frame name="resultFrame" src="http://<?php echo $ip ?>/tcf?cgi=emptyresult" frameborder="1">
</frameset>
</html>
