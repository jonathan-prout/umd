<html>
<head>
<meta http-equiv="refresh" content="1800">
<title>European Weather Radar</title>
<style>
#my-div
{
    width    : 600px;
    height   : 700px;
    overflow : hidden;
    position : relative;
}
 
#my-iframe
{
    position : absolute;
    top      : -250px;
    left     : -200px;
    width    : 1280px;
    height   : 1200px;
}
</style>
</head>
<body>
<font size="+1">European Weather Radar. Last refresh at <?php echo date(G), ":", date(i)  ?></font><br />
<table width="*" height="512" border="0" cellpadding="0">

    <td><img src="http://www.meteox.com/images.aspx?jaar=-3&voor=&soort=loop6uur&c=&n=&tijdid=<?php echo date(YnjGi) ?>" />
</td><td>
<div id="my-div">
<iframe src="http://www.meteocentrale.ch/en/weather/radar.html" id="my-iframe" scrolling="no" frameborder="no"></iframe>
</div>
</td>
</table>
<!-- http://www.meteox.com/images.aspx?jaar=-3&voor=&soort=loop24uur&c=&n=&tijdid=20118112113 -->
</body>
</html>

