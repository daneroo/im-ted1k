<?php
require_once 'facebook.php';

$now = time();
$stamp = date('Y-m-d',$now).'T'.date('H:i:s',$now).'Z';
#$graphurl = "http://chart.apis.google.com/chart?cht=lc&chs=180x120&chd=e:vCvCutw90y0e0Jzgxmx6kzijh6h6h6h6hmhmhRhmhmhmhmh6h6hmhmhmh6h6h6h6h6h6hmhmhmhRhRhRhRhRg9h6h6ijijijijiji4fXeFdwdwYpXXVcVcVc&chtt=Hour&chts=7f93bc,16&chco=3b5998&chxt=y&chxl=0:%7ckW%7c0.5%7c1.0%7c1.5%7c2.0";
#$fbml= "<img src='$graphurl' >";
$fbml='';
$fbml .= " Last Updated at ".$stamp;
echo "Update Facebook iMetrical refHandle:myhandle to:\n";
echo "  ".$fbml."\n";

// fb.fbml.setRefHandle('myhandle','Last Updated at %s'%stamp)

$appapikey = 'bd100b49340effa90332cdfbe6e85659';
$appsecret = 'b150ebbad9cdff51269248dbe4b9683d';
$facebook = new Facebook($appapikey, $appsecret);

$facebook->api_client->call_method('facebook.Fbml.setRefHandle', array( 'handle' => 'myhandle', 'fbml' => $fbml,) ); 

echo "Done\n"
?>


