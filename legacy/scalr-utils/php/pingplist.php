<?php
  //header("Content-type: text/xml");
header("Content-type: text/plain");


// xml declaration
$xmldecl = "<?xml version=\"1.0\"?>\n"; 
$xmldecl .= "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n";
echo $xmldecl;
$now = time();
$stamp = date('Y-m-d',$now).'T'.date('H:i:s',$now).'Z';
$REMOTEIP = $_SERVER['REMOTE_ADDR'];
$SERVER = $_SERVER['SERVER_NAME'];

echo "<plist version=\"1.0\"><dict>\n";
echo "<key>stamp</key><date>$stamp</date>\n";
echo "<key>server</key><string>$SERVER</string>\n";
echo "<key>remoteip</key><string>$REMOTEIP</string>\n";
echo "<key>status</key><integer>0</integer>\n";
echo "</dict></plist>\n";

?>