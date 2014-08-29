<?php
header("Content-type: text/plain");

/*
$url = 'http://aria.dl.sologlobe.com:9090/DashboardData';
$content = file_get_contents($url);
// first method
$xml = new SimpleXMLElement($content);

$kwnow =  (string)$xml->KWNow; // explicit string (not element)
$watt = 1000.0 * $kwnow;
*/





$xmldecl = "<?xml version=\"1.0\"?>\n"; 
$xmldecl .= "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n";
echo $xmldecl;

echo "<plist version=\"1.0\"><array>\n";
$numPoints=10;
$now = time();
$timeRange = 60*60*24; // in seconds
for ($i=0;$i<$numPoints;$i++) {
    $tt = $now - ($i/$numPoints)*$timeRange; 
    $nowstr = date('Y-m-d',$tt).'T'.date('H:i:s',$tt).'Z';
    //$watt = rand(1000,2000);
    $angle = ( fmod($now,60)/60.0 - $i/$numPoints )  * 6 * pi() ;
    $watt = round(5000.0 * (1+sin($angle))  );

    echo "<dict><key>stamp</key><date>$nowstr</date><key>value</key><integer>$watt</integer></dict>\n";
 }
echo "</array></plist>\n";
?>