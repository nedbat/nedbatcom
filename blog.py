#! /usr/bin/env python
"""Create a new blog entry."""

import os, re, string, sys, time

blogdir = r'~/web/stellated/blog'
blogfmt = \
"""<?xml version='1.0' encoding='utf-8'?>
<blog>
<entry when='%(now)s'>
<title>%(title)s</title>
<category></category>
<body>

<p>
</p>

</body>
</entry>
</blog>
"""

editor = r'/Applications/MacVim.app/Contents/MacOS/vim --servername VIM --remote-silent'

def keepChars(s, keep):
    return ''.join([c for c in s if c in keep])

fileok = string.ascii_letters + string.digits + '-'

slots = {}
slots['now'] = time.strftime("%Y%m%dT%H%M%S")

if len(sys.argv) > 1:
    outfile = '-'.join(sys.argv[1:]).replace(' ', '-')
    outfile = keepChars(outfile, fileok).lower()
    title = ' '.join(sys.argv[1:])
    slots['title'] = title[0].upper() + title[1:]
else:
    outfile = "blog_" + now
    slots['title'] = 'XXX'

if not outfile.endswith('.bx'):
    outfile = outfile + '.bx'

outfile = os.path.join(os.path.expanduser(blogdir), outfile)

if os.path.exists(outfile):
    print "%s already exists!" % outfile
else:
    print "Blogging to %s" % outfile
    open(outfile, 'w').write(blogfmt % slots)

os.system(editor+" "+outfile)
#os.spawnl(os.P_NOWAIT, editor, '"'+editor+'"', outfile)
