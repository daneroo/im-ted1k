<?php
  //header("Content-type: text/xml");
header("Content-type: text/plain");

// Parse params
//print "<!-- Scope param : ".htmlspecialchars($_GET["scope"])."  --> \n"; 
$scope=0;
$scope=intval(htmlspecialchars($_GET["scope"]));
if ($scope>4) $scope = fmod($scope,5);
if ($scope<0) $scope = fmod(intval(time()/10),5);

// Connect to db
$dbname = 'ted'; $dbhost = 'localhost'; $dbuser = 'aviso'; $dbpass = '';
$conn = mysql_connect($dbhost, $dbuser, $dbpass) or die ('Error connecting to mysql');
mysql_select_db($dbname);

function queryForTableSince($table,$since,$samples) {
    $query =  "select stamp,watt from $table ";
    if (!is_null($since)) { $query .= " where stamp<'$since'"; }
    $query .= " order by stamp desc";
    $query .= " limit $samples";
    //print "<!-- Query: ".$sql."  --> \n"; 
    return $query;
}

// this function also return le last stamp
function entriesForQuery($sql,$formatter) {
    $result = mysql_query($sql) or die('Query failed: ' . mysql_error());
    $lastStamp = '';
    while ($row = mysql_fetch_array($result, MYSQL_NUM)) {
        $stamp = substr($row[0],0,10).'T'.substr($row[0],-8).'Z';
        $lastStamp=$row[0];
        $watt = $row[1];
        $formatter($stamp,$watt);
    }
    mysql_free_result($result);
    return $lastStamp;
}

// formatters are used with 'Variable functions'
function plistRowFormatter($stamp,$watt) {
    echo "<dict><key>stamp</key><date>$stamp</date><key>value</key><integer>$watt</integer></dict>\n";
}
function observationtRowFormatter($stamp,$watt) {
    echo "<observation stamp='$stamp' value='$watt' />\n";
}

// might be called more than once ?
function entriesForTableSince($table,$since,$samples) {
    $sql = queryForTableSince($table,$since,$samples);
    $formatter = 'plistRowFormatter';
    //$formatter = 'observationtRowFormatter';
    return entriesForQuery( $sql ,$formatter);
}

function plist($scope) {
    // xml declaration
    $xmldecl = "<?xml version=\"1.0\"?>\n"; 
    $xmldecl .= "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n";
    echo $xmldecl;

    // plist header
    echo "<plist version=\"1.0\"><array>\n";
    //print "<!-- Scope value : $scope  --> \n"; 
    if ($scope == 0) { // Live
        $lastStamp = entriesForTableSince('watt',NULL,10);
        //print "<!-- LastStamp: ".$lastStamp."  --> \n"; 
        $lastStamp = entriesForTableSince('watt_tensec',$lastStamp,30);
    } elseif ($scope == 1) { // Hour
        $lastStamp = entriesForTableSince('watt_minute',NULL,60);
    } elseif ($scope == 2) { // Day
        $lastStamp = entriesForTableSince('watt_hour',NULL,48);
    } elseif ($scope == 3) { // Week
        $lastStamp = entriesForTableSince('watt_day',NULL,14);
    } elseif ($scope == 4) { // Month
        $lastStamp = entriesForTableSince('watt_day',NULL,62);
    }
    // plist footer
    echo "</array></plist>\n";
}

plist($scope);
mysql_close($conn);
?>