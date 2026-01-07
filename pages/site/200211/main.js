// Ned Batchelder's javascript helpers.
function nospam(user,domain,args) {
	loc = "mailto:" + user + "@" + domain;
	if (args) {
		loc += "?" + args;
	}
	window.location = loc;
}
/*
     FILE ARCHIVED ON 12:27:09 Dec 07, 2002 AND RETRIEVED FROM THE
     INTERNET ARCHIVE ON 13:22:22 Jan 07, 2026.
*/
