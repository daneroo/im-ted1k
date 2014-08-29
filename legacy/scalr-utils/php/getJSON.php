<?php
  // should be json mime type
  //header("Content-type: text/xml");
  header("Content-type: text/plain");

// Parse params
// get the day/date

// Connect to db
$dbname = 'ted'; $dbhost = 'localhost'; $dbuser = 'aviso'; $dbpass = '';
$conn = mysql_connect($dbhost, $dbuser, $dbpass) or die ('Error connecting to mysql');
mysql_select_db($dbname);

function queryForTableSince($table,$since,$samples) {
    $query =  "select stamp,watt from $table ";
    if (!is_null($since)) { $query .= " where stamp<'$since'"; }
    $query .= " order by stamp desc";
    $query .= " limit $samples";
    //print "<!-- Query: ".$query."  --> \n"; 
    return $query;
}

function entriesForQuery($sql) {
    $result = mysql_query($sql) or die('Query failed: ' . mysql_error());
    $obsarray = array();
    echo "[\n";
    while ($dico = mysql_fetch_assoc($result)) {
        //$stamp = substr($row[0],0,10).'T'.substr($row[0],-8).'Z';
        //$dico['stamp']= substr($dico['stamp'],0,10).'T'.substr($dico['stamp'],-8).'Z';
	// shorter overwrite char 10 with 'T' and append 'Z'
        $dico['stamp'][10] = 'T';
        $dico['stamp'] .= 'Z';
        echo "  ".json_encode($dico).",\n";
        $obsarray[]=$dico;
    }
    echo "]\n";

    //echo json_encode($obsarray);
    mysql_free_result($result);
}


// might be called more than once ?
function entriesForTableSince($table,$since,$samples) {
    $sql = queryForTableSince($table,$since,$samples);
    return entriesForQuery( $sql );
}


//entriesForTableSince('watt',null,86400);
entriesForTableSince('watt_tensec',null,8640);

mysql_close($conn);
?>