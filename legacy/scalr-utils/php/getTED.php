<?php
header("Content-type: text/plain");


$url = 'http://aria.dl.sologlobe.com:9090/DashboardData';
$content = file_get_contents($url);
// first method
$xml = new SimpleXMLElement($content);

$kwnow =  (string)$xml->KWNow; // explicit string (not element)
$watt = 1000.0 * $kwnow;

//$nowstr = date('c');  // alomost: 2008-11-11T02:15:11-05:00
// we want: 2008-11-11T10:12:19Z-0500
//$nowstr = date('Y-m-d').'T'.date('G:i:s').'Z'.date('O');
$nowstr = date('Y-m-d').'T'.date('G:i:s').'Z';



$xmldecl = "<?xml version=\"1.0\"?>\n"; 
$xmldecl .= "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n";
echo $xmldecl;

echo "<plist version=\"1.0\"><array>\n";
echo "<dict><key>stamp</key><date>$nowstr</date><key>value</key><integer>$watt</integer></dict>\n";
echo "</array></plist>";
?>