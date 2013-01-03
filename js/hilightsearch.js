jQuery.noConflict();
// Highlight search words on the page.
// http://nedbatchelder.com

/* From ftrain.com */
/* http://www.kryogenix.org/code/browser/searchhi/ */

/* Modified by Ned 20021006 to fix query string parsing and add case insensitivity. */
/* Modified by Ned 20051213 to ignore empty query string words. */

function highlightWord(node, word, colorindex) {
	// Iterate into this node's childNodes
	if (node.hasChildNodes) {
		var hi_cn;
		for (hi_cn = 0; hi_cn < node.childNodes.length; hi_cn++) {
			highlightWord(node.childNodes[hi_cn], word, colorindex);
		}
	}

	// And do this node itself
	if (node.nodeType == 3) { // text node
		var tempNodeVal = node.nodeValue.toLowerCase();
		tempWordVal = word.toLowerCase();
		if (tempNodeVal.indexOf(tempWordVal) != -1) {
			var pn = node.parentNode;
			if (pn.className.indexOf('searchword') != 0) {
				// word has not already been highlighted!
				var nv = node.nodeValue;
				var ni = tempNodeVal.indexOf(tempWordVal);
				// Create a load of replacement nodes
				var before = document.createTextNode(nv.substr(0,ni));
				var docWordVal = nv.substr(ni,word.length);
				var after = document.createTextNode(nv.substr(ni+word.length));
				var hiwordtext = document.createTextNode(docWordVal);
				var hiword = document.createElement("span");
				hiword.className = "searchword"+colorindex;
				hiword.appendChild(hiwordtext);
				pn.insertBefore(before,node);
				pn.insertBefore(hiword,node);
				pn.insertBefore(after,node);
				pn.removeChild(node);
			}
		}
	}
}

function welcomeSearch(words) {
	var si = document.getElementById("searchwelcome");
	si.className = "searchwelcome";
	var p = document.createElement("p");
	si.appendChild(p);
	var text = "Welcome.  You seem to have come here from a search engine. "
	if (words.length == 1) {
		text += "Your search word (" + words[0] + ") is highlighted on this page.";
	}
	else {
		text += "Your search words (" + words.join(' ') + ") are highlighted on this page.";
	}
	p.appendChild(document.createTextNode(text));
}

function filterArray(a, fnc) {
    var b = new Array();
    for (var i = 0; i < a.length; i++) {
        if (fnc(a[i])) {
            b.push(a[i]);
        }
    }
    return b;
}

function highlightSearch() {
	if (!document.createElement) {
		return;
	}
	var ref = document.referrer;
	if (ref.indexOf('?') == -1) {
		// No query in referrer.  For local testing, try for query in location.
		ref = ""+document.location;
		if (ref.indexOf('?highlight') == -1) {
			return;
		}
	}
	var qs = ref.substr(ref.indexOf('?')+1);
	var qsa = qs.split('&');
	for (i = 0; i < qsa.length; i++) {
		var qsip = qsa[i].split('=');
		if (qsip.length == 1) {
			continue;
		}
		// q= for Google, p= for Yahoo, qt= for LookSmart
		if (qsip[0].match(/\b(query|q|p|qt)\b/)) {
			var words = unescape(qsip[1].replace(/\+/g,' ')).split(/\s+/);
			words = filterArray(words, function (w) { return w != "";});
			if (words.length == 0) {
				continue;
			}
			// Sometimes people are redirected to the page by a search-like thing
			// which uses the URL as the &q= parameters.  Don't be tricked into
			// thinking it's a search term.
			if (words.length == 1) {
				if (words[0].match(/^http:\/\/[a-z.]*nedbatchelder\.com\/.*\.html$/)) {
					// Looks like a URL here.
					break;
				}
			}
			// Put a welcome message into the .searchwelcome div.
			welcomeSearch(words);
			// Highlight the words themselves.
			for (w = 0; w < words.length; w++) {
				highlightWord(document.getElementsByTagName("body")[0], words[w], w % 3);
			}
			// We've highlighted the search terms, no need to look further.
			break;
		}
	}
}

// Things to do when the page first loads.
jQuery(document).ready(highlightSearch);
