<?php
//
// Send the user someplace else.
//

if (isset($_GET["to"])) {
	Header("Location: ".$_GET["to"]); 
	exit; 
}
?>

<body>
<p>Where do you want to go today?</p>
</body>
