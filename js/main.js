// Ned Batchelder's Javascript code.
// http://nedbatchelder.com

function nospam(user,domain,args) {
	var ch = String.fromCharCode;
	var loc = "ma" + ch(105) + "lto" + ch(58) + user + ch(64) + domain;
	if (args) {
		loc += "?" + args;
	}
	window.location = loc;
}
