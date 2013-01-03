""" Delete directories to make room on the disk.
    Ned Batchelder, http://www.nedbatchelder.com
    Sept 10, 2003
"""

usage = """
Delete directories to make room on the disk.
Usage: makeroom [OPTS] DIR
DIR is the directory whose children can be deleted to make room.

Options:
    -s BYTES    Set BYTES as the needed free space.
                You can use expressions like 2*G for 2 gig.
                Default is 1*G.
"""

import getopt, path, sys

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def diskFreeSpace(path):
    import win32file
    ppath = path.parent
    while ppath != ppath.parent:
        ppath = ppath.parent
    secPerClu, bytePerSec, freeClu, totClu = win32file.GetDiskFreeSpace(ppath)
    return secPerClu * bytePerSec * freeClu

def removeTree(path):
    # rmtree can't do readonly files, so set them all writable first.
    for f in path.walkfiles():
        f.chmod(0666)
    path.rmtree(True)
    
def main(argv):
    try:
        if '-?' in argv:
            print usage
            return

        if len(argv) < 2:
            raise Usage("Not enough arguments")

        argv0 = argv.pop(0)

        # Default the options.        
        sizeNeeded = 1024*1024*1024
        
        try:
            opts, args = getopt.getopt(argv, 's:')
        except getopt.error, msg:
            raise Usage(msg)
    
        for o, a in opts:
            if o == '-s':
                K = 1024
                M = K*K
                G = K*M
                sizeNeeded = eval(a)
            else:
                raise Usage("Don't understand argument %s" % o)

        # Read the arguments
        if len(args) < 1:
            raise Usage("Need a root directory")
        root = path.path(args[0])

        #print "root = %s, size = %d" % (root, sizeNeeded)
        print "disk free = %d" % (diskFreeSpace(root),)
        
        # Get the list of all child directories of root.
        childDirs = [ (d.mtime, d) for d in root.dirs() ]
        childDirs.sort()
        for t, d in childDirs:
            print d, t

        # Loop, deleting children until the target is met.
        while diskFreeSpace(root) < sizeNeeded:
            if len(childDirs) == 0:
                print "No directories to delete!"
                return 0
            oldestChild = childDirs.pop(0)[1]
            if (oldestChild/"keep.txt").exists():
                print "%s is marked for keeping" % (oldestChild,)
                continue
            print "Deleting %s.." % (oldestChild,)
            try:
                removeTree(oldestChild)
            except:
                import traceback
                extype, exvalue = sys.exc_info()[:2]
                exmsg = traceback.format_exception_only(extype, exvalue)
                print >>sys.stderr, "Couldn't delete %s: %s" % (oldestChild, ''.join(exmsg))

        return 1
    
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "(for help use -?)"
        return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
