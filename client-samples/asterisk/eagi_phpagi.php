#!/usr/bin/php -q
<?php
/*
 * @author mihail.belobrov@gmail.com
 * For FreePBX
 */
ob_implicit_flush(false);
set_time_limit(0);
error_reporting(0);
 
$VersionPath    = dirname(__FILE__);
$LibPath        = $VersionPath.'/lib';

$voskServer = 'ws://127.0.0.1:2700';
$FD3 = 'php://fd/3';
require_once '/etc/freepbx.conf'; // Configure DB and other things
require_once '/var/lib/asterisk/agi-bin/phpagi.php'; // Load php-agi in FreePBX

$module_name	= 'eagiVosk';

$dbh = \FreePBX::Database(); // Connect to database
$outGoingPath = \FreePBX::Config()->get("ASTSPOOLDIR")."/outgoing"; // Recieve FreePBX settings
$monitorPath = \FreePBX::Config()->get("ASTSPOOLDIR")."/monitor"; // Call recordings storage

// Keywords for call directions
$word_arr = array(
		'tech' => 'ext-queues,8001,1',  	 // queue 8001
		'accountant' => 'from-did-direct,102,1', // accountant 202
		'operator' => 'ext-queues,800,1',	 // quue 800
);

$myagi = new AGI();
$myagi->answer();

// Loads websocket library
require_once("/var/www/html/tts/vosk/scripts/websocket-php-1.3.1/vendor/autoload.php"); 
use WebSocket\Client;
$client = new Client($voskServer, array('timeout' => 20,'fragment_size'=> 8192));
$client->send('{ "config" : { "sample_rate" : 8000 } }', 'text');

// Play hello sound
$myagi->exec('PLAYBACK',array('/var/lib/asterisk/sounds/ru/hello-world'));

$myText = array();
$totalText = '';
$mydata = fopen($FD3, "rb"); // opens file descriptor 3
$previous_text = '';
while(!feof($mydata)) {
	$data = fread($mydata,8192);
	$client->send($data, 'binary');
	$receive = $client->receive();
	
	$result = json_decode($receive, true);
	if(!empty($result['partial'])) {
		$myagi->verbose($result['partial'],3);
		if($previous_text != $result['partial']){
			$previous_text = $result['partial'];
			foreach ($word_arr as $word => $destination){
				if (preg_match('/'.$word.'/u', $previous_text , $matches) ){
					list($context,$ext,$priority) = explode(',',$destination);
					$myagi->exec_dial('Local',$ext.'@'.$context); // calls required direction
					break;
				}
			}
			
		}
		
	}
}
$client->send("{\"eof\" : 1}");
$receive = $client->receive();
fclose($mydata);

$myagi->hangup(); 
?>
