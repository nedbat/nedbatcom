""" Blame All for svn, like p4 annotate -a.
    Ned Batchelder.
    http://nedbatchelder.com/code/utilities/blameall.html
    
    Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""

from difflib import SequenceMatcher
import optparse, re, subprocess, sys

__version__ = '1.1.20071201'

class MultiDiff:
    """ Accumulates successive revisions of a text, and produces a comprehensive
        version with each line labelled with revisions.  All versions of each
        line are included.
    """
    def __init__(self):
        self.last_lines = None
        self.bdelta = 0
        self.cdelta = 0
    
    def add_rev(self, rev, lines):
        if self.last_lines is None:
            self.blame = [ [rev, rev, l] for l in lines ]
            self.curlines = range(len(lines))
        else:
            self.next_lines = lines
            self.next_rev = rev
            self.bdelta = 0
            self.cdelta = 0
            s = SequenceMatcher(None, self.last_lines, self.next_lines)
            for opcode in s.get_opcodes():
                op, i1, i2, j1, j2 = opcode
                getattr(self, '_opcode_'+op)(i1, i2, j1, j2)
        self.last_lines = lines
    
    def _new_lines(self, j1, j2):
        newlines = []
        for j in range(j1, j2):
            newlines.append([self.next_rev, self.next_rev, self.next_lines[j]])
        return newlines
    
    def _opcode_equal(self, i1, i2, j1, j2):
        for i in range(i1, i2):
            ci = i + self.cdelta
            self.curlines[ci] += self.bdelta
            self.blame[self.curlines[ci]][1] = self.next_rev
    
    def _bi(self, ci):
        if ci < len(self.curlines):
            bi = self.curlines[ci]+self.bdelta
        else:
            assert ci == len(self.curlines)
            bi = len(self.blame)
        return bi
    
    def _multipurpose(self, i1, i2, j1, j2):
        newlines = self._new_lines(j1, j2)
        
        idel = i2-i1
        jdel = j2-j1
        bdel = cdel = 0
        
        # Part one: replace the lines in the common part
        com = min(idel, jdel)
        for i in range(com):
            ci = i1+i+self.cdelta
            bi = self._bi(ci)+1
            bi = min(bi, len(self.blame))
            self.blame[bi:bi] = [newlines[i]]
            self.curlines[ci] = bi
            self.bdelta += 1
            
        # Part two: if j is longer, then insert the j lines
        if idel < jdel:
            ci = i1+com+self.cdelta
            bi = self._bi(ci)
            bi = min(bi, len(self.blame))
            self.curlines[ci:ci] = range(bi, bi+jdel-com)
            self.blame[bi:bi] = newlines[com:]
            bdel += jdel-com
            cdel += jdel-com
            
        # Part three: if i is longer, delete the i lines
        if idel > jdel:
            del self.curlines[i1+com+self.cdelta:i2+self.cdelta]
            cdel -= idel-com
            
        self.cdelta += cdel
        self.bdelta += bdel
    
    _opcode_insert = _multipurpose
    _opcode_delete = _multipurpose
    _opcode_replace = _multipurpose

    def blame_data(self):
        return self.blame
    
def doit(cmd):
    #print cmd
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).stdout
    return out.read()

def get_revs_for_file(fpath, revarg=None):
    """ Returns a list of revisions for a file.
        The return looks like [(17, 'ned'), (23, 'joe'), (199, 'sally')]
    """
    revs = []
    if revarg:
        dashr = ' -r' + revarg
    else:
        dashr = ''
    log = doit("svn log%s %s" % (dashr, fpath)).split('\n')
    while log:
        log.pop(0)  # Toss the separator
        revline = log.pop(0)
        if not revline and not log:
            # End of the log.
            break
        m = re.match(r"r(?P<rev>[0-9]+) \| (?P<user>[^|]+) \| [^|]+ \| (?P<lines>[0-9]+) line.*", revline)
        if not m:
            raise Exception("Couldn't scrape log line: %r\nRemaining: %r" % (revline, log))
        revs.append((int(m.group('rev')), m.group('user')))
        for i in range(int(m.group('lines'))+1):
            log.pop(0)
    revs.sort()
    return revs

def get_rev_file(fpath, rev):
    """ Get the text of a particular revision of a file.
        The text is slightly cleaned to avoid bogus comparisons.
    """
    text = doit("svn cat -r%d %s" % (rev, fpath))
    return text.replace('\r', '').split('\n')

def main(argv):
    # Parse the command line options
    parser = optparse.OptionParser(
        usage="%prog [options] [path]",
        description="blameall is like svn blame, but it outputs every line in every revision."
    )
    parser.add_option("-r", "--revision", dest="revision", help="the revision range to include")

    options, args = parser.parse_args(argv)

    revarg = rev1 = None
    revn = 'head'
    if options.revision:
        if ':' in options.revision:
            revarg = options.revision
            rev1, revn = options.revision.split(':')
        else:
            revarg = options.revision + ":head"
            rev1 = options.revision
            
    if not args:
        print >>sys.stderr, "Need a file path to work on"
        return
    if len(args) > 1:
        print >>sys.stderr, "Can only work on one file at a time"
        return

    fpath = args[0]
    
    # Get the list of revisions to compare.
    revs = get_revs_for_file(fpath, revarg)
    if rev1 and rev1 != '1':
        revs = [(int(rev1), '???')] + revs

    # Load up the MultiDiff with all the text.
    multidiff = MultiDiff()
    for i, (rev, user) in enumerate(revs):
        print >>sys.stderr, rev,
        text = get_rev_file(fpath, rev)
        multidiff.add_rev(i, text)
        
    # Print the resulting combined file.
    print >>sys.stderr
    for i1, i2, line in multidiff.blame_data():
        r1 = revs[i1][0]
        if i2 == len(revs)-1:
            r2 = revn
        else:
            r2 = revs[i2+1][0]-1
        print "%5s %5s %s" % (r1, r2, line)

if __name__ == '__main__':
    main(sys.argv[1:])

# History:
# 2007-11-28: First version.
# 2007-12-01: Updated the author name matching regex to allow spaces.
