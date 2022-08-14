<?php
session_start();

$json = file_get_contents('php://input');
file_put_contents('json.txt', $json);

$jsonout = (json_decode($json,true));

$profile_id = ($jsonout['profile_id']);
$bottom = ($jsonout['bottom']);
$top = ($jsonout['top']);

$email = ($jsonout['email']);
$id = ($jsonout['id']);

$file = ($jsonout['file']);
$sep = ($jsonout['sep']);

$data = "{$profile_id}{$sep}0{$sep}false{$sep}{$bottom}{$sep}{$top}{$sep}{$id}{$sep}{$email}\n";
$fp = fopen($file, 'a');
fwrite($fp, $data);

?>
