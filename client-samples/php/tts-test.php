<?php

require_once("./vendor/autoload.php");

$url = 'https://api.alphacephei.com/tts';
$data = array('text' => 'Hello world!');

$options = array(
    'http' => array(
        'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
        'method'  => 'POST',
        'content' => http_build_query($data)
    )
);
$context  = stream_context_create($options);
$result = file_get_contents($url, false, $context);
if ($result === FALSE) { /* Handle error */ }
file_put_contents("tts.wav", $result);
?>
