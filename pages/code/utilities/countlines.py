"""
countlines: count the lines in a tree of files.

Ned Batchelder, 12/2000
http://www.nedbatchelder.com

requires Python 2.0
"""

import fnmatch, os

# A dict mapping extensions to line counts

linecounts = {}
totallines = 0

# A dict mapping extenstions to file counts

filecounts = {}
totalfiles = 0

# Directory patterns to ignore

ignoreDirs = [ 'CVS' ]

# File patterns to ignore

ignoreFiles = [ '.#*' ]

# Get the extension of a file path

def extension(path):
    dot = path.rfind('.')
    if dot == -1:
        return ""
    else:
        return path[dot:]

# count the lines in a file

def countFile(path):
    nLines = 0
    try:
        f = open(path, 'r')
        nLines = len(f.readlines())
    except IOError:
        pass
    return nLines

# Should we ignore this file?

def ignore(f, pats):
    for ig in pats:
        if fnmatch.fnmatch(f, ig):
            return 1
    return 0

# process a directory

def countDir(dir):
    global filecounts, linecounts, totalfiles, totallines

    try:
        files = os.listdir(dir)
    except:
        return

    for f in files:
        fullf = os.path.join(dir, f)
        if os.path.isdir(fullf):
            if not ignore(f, ignoreDirs):
                countDir(fullf)
        else:
            if not ignore(f, ignoreFiles):
                ext = extension(f)
                filecounts[ext] = filecounts.get(ext, 0) + 1
                totalfiles = totalfiles + 1

                lines = countFile(fullf)
                linecounts[ext] = linecounts.get(ext, 0) + lines
                totallines += lines

def printCounts():
    fmt = '%12s %5s %8s'
    exts = filecounts.keys()
    exts.sort()
    print fmt % ('ext', 'files', 'lines')
    for e in exts:
        print fmt % (e, filecounts[e], linecounts[e])
    print fmt % ('==total==', totalfiles, totallines)

if __name__ == '__main__':
    countDir('.')
    printCounts()

# History:
# 10/26/2001: Protection against not being able to read a file.
