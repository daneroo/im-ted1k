<?php
header("Content-type: text/plain");
$dbhost = 'localhost';
$dbuser = 'aviso';
$dbpass = '';

$conn = mysql_connect($dbhost, $dbuser, $dbpass) or die                      ('Error connecting to mysql');

$dbname = 'ted';
mysql_select_db($dbname);

$xmldecl = "<?xml version=\"1.0\"?>\n"; 
$xmldecl .= "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n";
echo $xmldecl;

echo "<plist version=\"1.0\"><array>\n";
# old live query
#$query = 'SELECT unix_timestamp(stamp),watt FROM tedlive order by stamp desc limit 30';
//print "<!-- Scope param : ".htmlspecialchars($_GET["scope"])."  --> \n"; 
$scope=0;
$scope=intval(htmlspecialchars($_GET["scope"]));
if ($scope>4) $scope = fmod($scope,5);
if ($scope<0) $scope = fmod(intval(time()/10),5);
//print "<!-- Scope value : $scope  --> \n"; 

if ($scope == 0) {
    $table = 'watt';         $secondsPerSample=1;      $samples=180;  // live
 } elseif ($scope == 1) {
    $table = 'watt_tensec';  $secondsPerSample=10;     $samples=300;  // minutes
 } elseif ($scope == 2) {
    $table = 'watt_minute';  $secondsPerSample=60;     $samples=60;  // hour
 } elseif ($scope == 3) {
    $table = 'watt_hour';    $secondsPerSample=3600;   $samples=48;  // day
 } elseif ($scope == 4) {
    $table = 'watt_day';     $secondsPerSample=86400;  $samples=62;  // MOnth
 }

$secondsInWhere = $secondsPerSample * (1+$samples);
$query = "select stamp,watt from $table order by stamp desc limit $samples";
//print "<!-- Query: ".$query."  --> \n"; 

$result = mysql_query($query) or die('Query failed: ' . mysql_error());

while ($row = mysql_fetch_array($result, MYSQL_NUM)) {
    $watt = $row[1];
    $stamp = substr($row[0],0,10).'T'.substr($row[0],-8).'Z';
    //$tt = $row[0];
    //$stamp = date('Y-m-d',$tt).'T'.date('H:i:s',$tt).'Z';
    echo "<dict><key>stamp</key><date>$stamp</date><key>value</key><integer>$watt</integer></dict>\n";
}

// Free resultset
mysql_free_result($result);

echo "</array></plist>\n";

mysql_close($conn);
?>