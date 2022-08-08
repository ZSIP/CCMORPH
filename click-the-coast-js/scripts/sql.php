<?php
$conn = pg_connect("host=localhost port=5432 dbname=klikaczu user=florapom password=urticaDactylis");
      $sql = "INSERT INTO public.punkty (email, identyfikator, x, y, image) VALUES('email', 'id', 'x', 'y', 'image')";
      $result = @pg_exec($conn, $sql) or die (pg_errormessage());

?>