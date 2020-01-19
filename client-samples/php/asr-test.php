<?php

require_once("./vendor/autoload.php");

use WebSocket\Client;

$client = new Client("wss://api.alphacephei.com/asr/en/", array('timeout' => 200));
$myfile = fopen("test.wav", "r");
while(!feof($myfile)) {
   $data = fread($myfile, 8000);
   $client->send($data, 'binary');
   echo $client->receive() . "\n";
}
$client->send("{\"eof\" : 1}");
echo $client->receive() . "\n";
fclose($myfile);

?>
