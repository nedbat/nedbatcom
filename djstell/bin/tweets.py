import sys
import os
import time
import datetime
import twitter
import re
import urllib2

def main():
	api = twitter.Api()
	statuses = api.GetUserTimeline('nedbat', count=60)
	f = start()
	global alt
	alt = False

	for s in statuses:
		if s.GetInReplyToScreenName():
			# Don't include replies.
			continue
		#date = "Fri May 07 11:53:49 +0000 2010"
		oldStringBits = s.created_at.split(" ")
		newString = " ".join(oldStringBits[1:])
		curDate = time.strptime(newString, "%b %d %H:%M:%S +0000 %Y")	
		dateString = time.strftime("%b %d", curDate)
		
		text = s.text
		text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
		text = doBitly(text)
		text = doLinks(text)
		text = doReplies(text)
		text = doHashes(text)
		#text = doRT(text)
		text += (" <a href='http://twitter.com/nedbat/status/%s' class='date'>(" % s.GetId()) + dateString + ")</a>"
		text = '<span class="tweet">' + text + '</span>'
		writeOut(text, f)
		print text
		print
		
	finish(f)


def doReplies(inString):
	out = re.sub(r'@([a-zA-Z0-9_]+)', r'<a class="user" href="http://www.twitter.com/\1">@\1</a>', inString)
	return out
	
def doLinks(inString):
	out = re.sub(r'(http://[-a-zA-Z0-9._/?=]+)', r'<a href="\1">\1</a>', inString)
	return out

short_domains = [
	"bit.ly", "icio.us",
	]
	
def doBitly(inString):
	#print "looking for bit.ly links!"
	bits = inString.split()
	i = 0
	while i < len(bits):
		b = bits[i]
		is_short = False
		for short in short_domains:
			if short in b:
				is_short = True
		if is_short:
			#print "found a shortened link: "+b
			try:
				fp = urllib2.urlopen(b)
				bits[i] = fp.geturl()
				#print "actual url is "+bits[i]
			except urllib2.HTTPError:
				#print "couldn't get actual url"
				pass
		i += 1
	out = " ".join(bits)
	return out
	
	
def doHashes(inString):
	out = re.sub(r'#([a-zA-Z0-9_]+)', r'<a class="hashtag" href="http://www.twitter.com/#search?q=%23\1">#\1</a>', inString)
	return out
	
def doRT(inString):
	if "RT" in inString:
		return '<div class="rt">' + inString + '</div>'
	else:
		return '<div class="tweet">' + inString + '</div>'
	
PROLOG = """\
<?xml version="1.0" encoding="utf-8"?>
<blog>
<entry when="%s">
<title>Recent tweets</title>
<category>quick</category>
<body>
"""

EPILOG = """\
</body>
</entry>
</blog>
"""

def start():
	isonow = time.strftime("%Y%m%dT%H%M%S")
	f = open('blog/tweets_%s.bx' % isonow[:8], 'w')
	f.write(PROLOG % isonow)
	return f
	
def writeOut(inString, file):
	file.write("<quick>"+inString+"</quick>\n")
	
def finish(file):
	file.write(EPILOG)
	file.close()
	print("Successfully wrote file")
	
if __name__ == "__main__":
	main()
