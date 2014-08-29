<?php
$outfile = fopen("/tmp/weightrical.xml", "w");
$infile = fopen("php://input", "rb");
/* Read the data 1 KB at a time
 and write to the file */
while ($data = fread($infile, 1024))
    fwrite($outfile, $data);
fclose($fp);
fclose($putdata);
?> 