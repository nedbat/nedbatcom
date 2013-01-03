"""
wh: a 'where' command that actually is useful on Win32
It understands the PATH and PATHEXT environment variables.

Ned Batchelder, http://nedbatchelder.com

2001-10-21: First version
2002-10-08: Can use other environments than PATH or PATHEXT.
2003-12-01: More helpful usage message, printed more often.
"""

import getopt, os, os.path, sys

def usage():
    print "wh.py [OPTIONS] commandname"
    print "Prints full filenames of executables that will be run when"
    print "commandname is used as a command in the shell."
    print "Options:"
    print " -p PATH            Environment variable for path"
    print " -p dir;dir;dir     Use this path"
    print " -e PATHEXT         Environment variable for extensions"
    print " -e .a;.b;.c        Use these extensions"
    sys.exit(2)
    
pathsrc = "PATH"        # Where to get the path
pathextsrc = "PATHEXT"  # Where to get the extension list
dotfirst = 1            # Should we look in the current directory also?

try:
    opts, args = getopt.getopt(sys.argv[1:], "p:e:")
except getopt.GetoptError:
    # print help information and exit:
    usage()

if not args:
    usage()

for o, a in opts:
    if o == '-p':
        pathsrc = a
        dotfirst = 0
    if o == '-e':
        pathextsrc = a

if ';' in pathsrc:
    path = pathsrc
else:
    path = os.environ[pathsrc]
path = filter(None, path.split(";"))

if dotfirst:
    path = ["."]+path
    
if ';' in pathextsrc:
    pathext = pathextsrc
else:
    pathext = os.environ[pathextsrc]
pathext = filter(None, pathext.split(";"))

# The command name we are looking for
cmdName = args[0]

# Is the command name really a file name?
if '.' in cmdName:
    # Fake it by making pathext a list of one empty string.
    pathext = ['']

# Loop over the directories on the path, looking for the file.

for d in path:
    for e in pathext:
        filePath = os.path.join(d, cmdName + e)
        if os.path.exists(filePath):
            print filePath

#end.
