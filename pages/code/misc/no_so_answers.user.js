// ==UserScript==
// @name           No answering on Stackoverflow
// @namespace      http://nedbatchelder.com/greasemonkey
// @description    Hide the answer box on Stack Overflow to stop obsessive behavior
// @include        http://stackoverflow.com/*
// ==/UserScript==
	
GM_addStyle(
	"@namespace url(http://www.w3.org/1999/xhtml); " +
	".question-page #post-form { display: none; }"
	);
