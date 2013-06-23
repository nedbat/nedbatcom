<?php
// Redirector for old extended blog entries to their new locations.

$oldnew = array(
    {% for e in entries %}
	"/blog/{{e.when|date:"Ymd\THis"}}.html" => "{{e.get_absolute_url}}"{% if not forloop.last %},{% endif %}
    {% endfor %}
);

$path = $_SERVER["REQUEST_URI"];

$redir = $oldnew[$path];
if ($redir == "") {
	$redir = "/blog/index.html";
}

header("Location: $redir",TRUE,301);
?>
