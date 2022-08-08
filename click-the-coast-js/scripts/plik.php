<?php
session_start();

$json = file_get_contents('php://input');

echo($json);
$conn = pg_connect("host=localhost port=5432 dbname=klikaczu user=florapom password=urticaDactylis");


$jsonout = (json_decode($json,true));
print_r($jsonout);
$ax= ($jsonout[points][0][0]);


echo($id_user);

$i = 0;
while ($i <= count($jsonout['profile'])-1)
{
$ay= ($jsonout[points][0][1]);
$bx= ($jsonout[points][1][0]);
$by= ($jsonout[points][1][1]);
$profile= ($jsonout[profile]);
$email= ($jsonout[email]);
$id_user= ($jsonout[id]);
   echo($x);
      $sql = "INSERT INTO public.wydmy (ax, ay, bx, by, profile, email, id_user) VALUES($ax, $ay, $bx, $by, '$profile', '$email', '$id_user')";
      $result = @pg_exec($conn, $sql) or die (pg_errormessage());
   
   $i++;

}
?>
