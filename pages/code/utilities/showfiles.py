"""Simple file lister to show me what I want to see.
Ned Batchelder, 12/14/2001
http://www.nedbatchelder.com
"""

import getopt
import os
import string
import sys
import time
from stat import *

if os.name == 'nt':
    import win32file
    def fileAttr(f, dummy):
        ret = ''
        attr = win32file.GetFileAttributes(f)
        attrs = [
            (win32file.FILE_ATTRIBUTE_READONLY, 'r'),
            (win32file.FILE_ATTRIBUTE_HIDDEN,   'h'),
            (win32file.FILE_ATTRIBUTE_SYSTEM,   's')
            ]
        for bit, char in attrs:
            if attr & bit:
                ret += char
            else:
                ret += ' '
        return ret

else:
    def fileAttr(f, s):
        return '   '

def formatTime(secs):
    tup = time.localtime(secs)
    ret = time.strftime('%m/%d/%y %I:%M:%S', tup)
    if tup[3] >= 12:
        if tup[3] == 12 and tup[4] == 0:
            ret += 'n'  # noon
        else:
            ret += 'p'  # pm
    else:
        if tup[3] == 0 and tup[4] == 0:
            ret += 'm'  # midnight
        else:
            ret += 'a'  # am
    return ret

def formatSize(size):
    """Format a size for display"""
    # There ought to be an easier way to do this.
    sl = [c for c in str(size)]
    for i in range(len(sl)-3, 0, -3):
        sl[i:i] = [',']
    return string.join(sl, '')

lineformat = '%18s %3s %11s %s'
totalformat = '= %s bytes, %s files'

class FileEntry:
    def __init__(self, filespec):
        """
        Create a FileEntry from either a string, or a pair of strings
        (directory, file).
        """
        if type(filespec) == type(()):
            self.dir, self.name = filespec
            self.path = os.path.join(*filespec)
        else:
            self.dir = '.'
            self.name = filespec
            self.path = filespec
            
        stat = os.stat(self.path)
        self.size = stat[ST_SIZE]
        self.mod = stat[ST_MTIME]
        self.isDir = S_ISDIR(stat[ST_MODE])
        self.attr = fileAttr(self.path, stat)
        
    def __str__(self):
        mod = formatTime(self.mod)
        size = formatSize(self.size)
        if self.isDir:
            size = '/'
        return lineformat % (mod, self.attr, size, self.name)

    def lcaseName(self):
        return string.lower(self.name)
    
def nameCompare(e1, e2):
    """Case=insensitive compare"""
    if e1.isDir and not e2.isDir:
        return -1
    if e2.isDir and not e1.isDir:
        return 1
    
    s1 = e1.lcaseName()
    s2 = e2.lcaseName()
    if s1 == s2:
        return 0
    elif s1 < s2:
        return -1
    else:
        return 1

def sizeCompare(e1, e2):
    """Compare by size"""
    if e1.size < e2.size:
        return -1
    elif e1.size > e2.size:
        return 0
    else:
        return 1
    
def dateCompare(e1, e2):
    """Compare by date"""
    if e1.mod < e2.mod:
        return -1
    elif e1.mod > e2.mod:
        return 0
    else:
        return 1

def starify(s):
    return [ i*'*/'+s for i in range(10) ]
        
def glue(l):
    """Glue the elements of a list together: [[1,2], [3,4]] --> [1,2,3,4]"""
    return reduce(lambda a,b: a+b, l)

def main(args):

    def usage():
        print '-od -os -d -s -r'
        sys.exit()
        
    try:
        opts, args = getopt.getopt(args, "o:dsr")
    except getopt.GetoptError:
        # print help information and exit:
        usage()

    # Collect the options
    
    sortfn = nameCompare
    glob = None
    deep = 0
    
    for o, a in opts:
        if o == '-o':
            if a == 'd':
                sortfn = dateCompare
            elif a == 's':
                sortfn = sizeCompare
            else:
                usage()
        elif o == '-d':
            sortfn = dateCompare
        elif o == '-s':
            sortfn = sizeCompare
        elif o == '-r':
            deep = 1
        else:
            usage()

    # Collect the files
    
    files = []

    specs = args or ['*']
    
    if deep:
        specs = glue([starify(s) for s in specs])

    for a in specs:
        bFile = os.access(a, os.F_OK)
        if bFile:
            stat = os.stat(a)
            if S_ISDIR(stat[ST_MODE]):
                newFiles = os.listdir(a)
                if a != '.':
                    newFiles = map((lambda f,d=a: (d, f)), newFiles)
                files += newFiles
            else:
                files += [a]
        else:
            import glob
            files += glob.glob(a)

    entries = [ FileEntry(f) for f in files ]

    # Sort the entries
    
    entries.sort(sortfn)

    # Print the entries
    
    totsize = 0
    nfiles = 0
    for e in entries:
        totsize += e.size
        nfiles += 1
        print str(e)
        
    print totalformat % (formatSize(totsize), nfiles)

if __name__ == '__main__':
    main(sys.argv[1:])
