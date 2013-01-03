<?php
//
// Serve different home pages for different host names.
// Ned Batchelder, http://www.nedbatchelder.com
//

ini_set("track_errors", "1");	// Get errors into $php_errormsg.

$defaulthome = "index.html";

$homes = array(
	"maxib1.com" => "mzb/index.html",
	"stickfus.com" => "stickfus.html",
	"maxbatchelder.com" => "maxbatchelder.html"
);

$host = $_SERVER["HTTP_HOST"];
$host = preg_replace("/^www[.]/", "", $host);

$homepage = $homes[$host];
if ($homepage == "") {
	$homepage = $defaulthome;
}

if (!@include('./'.$homepage)) {
	echo "<!-- Couldn't read '$homepage': $php_errormsg -->\n";
	include('./'.$defaulthome);
}

?>
