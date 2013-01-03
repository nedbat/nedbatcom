#! /usr/bin/python
# readurl.py - read a URL.
#
# Ned Batchelder
# http://www.nedbatchelder.com

import getopt, sys, urllib

__version__ = "1.1.20040207"

class MyUrlOpener(urllib.FancyURLopener):
    def __init__(self, *args):
        self.version = "readurl.py (www.nedbatchelder.com)"
        urllib.FancyURLopener.__init__(self, *args)

urllib._urlopener = MyUrlOpener()

def readurl(url, header=1, content=1, showurl=0, hexcontent=0):
    furl = urllib.urlopen(url)
    if showurl:
        print "URL retrieved:", furl.geturl()
    if header:
        print furl.info()
    if hexcontent:
        import hexdump
        hexdump.hexdump(furl)
    elif content:
        print furl.read()
    
def main(args):

    def usage():
        for l in [
            "readurl: read and display the data at a URL",
            "readurl [OPTS] URL",
            "URL is a full URL, including the scheme, such as http://cnn.com",
            "OPTS:",
            " -h          show the headers",
            " -c          show the page content",
            " -x          show the page content in hex",
            " -u          show the real URL retrieved",
            ]: print l
        sys.exit()
        
    try:
        opts, args = getopt.getopt(args, "hcxu")
    except getopt.GetoptError:
        # print help information and exit:
        usage()

    options = {}

    header = 0
    content = 0
    showurl = 0
    
    for o, a in opts:
        if o == '-h':
            header = 1
        elif o == '-c':
            content = 1
        elif o == '-x':
            options['hexcontent'] = 1
        elif o == '-u':
            showurl = 1
        else:
            usage()

    if not header and not content and not showurl:
        content = 1

    options['header'] = header
    options['content'] = content
    options['showurl'] = showurl
    
    if len(args) == 0:
        usage()
    else:
        for url in args:
            readurl(url, **options)
        
if __name__ == '__main__':
    main(sys.argv[1:])
