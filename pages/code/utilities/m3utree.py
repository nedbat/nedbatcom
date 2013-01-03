""" Create a tree of .m3u files, one for each directory in the tree,
    containing all the .mp3 files in the subtree rooted there.
    Ned Batchelder, http://nedbatchelder.com
"""

__version__ = '1.3.20040113'    # History at the end of the file.

# Imports you may need from somewhere non-standard.
import path         # std, or from http://www.jorendorff.com/articles/python/path
import id3reader    # from http://nedbatchelder.com/code/modules/id3reader.html

try:
    import mp3      # from http://ibofobi.dk/svn/Jukebox/jukebox/mp3.py
    _bHaveMp3 = 1
except:
    _bHaveMp3 = 0

# standard Python modules
import sys, traceback

try:
    sum
except NameError:
    def sum(l):
        return reduce((lambda x, y: x+y), l)

# Safe printing: can print any unicode string
def safeprint(msg):
    msg = msg.encode(sys.getdefaultencoding(), 'replace')
    if msg[-1] == '\n':
        msg = msg[:-1]
    print msg

# A stack of .m3u files.
m3us = []

def mp3secs(mp3file):
    secs = 0
    if _bHaveMp3:
        secs = sum([mp3.time(h) for h,f in mp3.frames(mp3file)])
    return secs

def formatException():
    extype, exvalue = sys.exc_info()[:2]
    exmsg = traceback.format_exception_only(extype, exvalue)
    return ''.join(exmsg)

def getM3uString(fname):
    mp3file = open(fname, 'rb')

    caption, performer, title = '','',''
    try:
        mp3file.seek(0)
        id3 = id3reader.Reader(mp3file)
        performer = id3.getValue('performer')
        title = id3.getValue('title')
    except:
        safeprint("Couldn't read ID3 tag in file %s: %s" % (fname, formatException()))

    if performer:
        caption += performer
    if title:
        if caption:
            caption += ' - '
        caption += title

    extinf = ''
    if caption:
        secs = 0
        try:
            mp3file.seek(0)
            secs = mp3secs(mp3file)
        except:
            safeprint("Couldn't read MP3 file %s: %s" % (fname, formatException()))

        if isinstance(caption, type(u'')):
            caption = caption.encode('iso8859-1', 'replace')

        extinf = '#EXTINF:%d,%s\n' % (int(secs), caption)
        
    mp3file.close()
    
    fpath = fname.abspath()
    if isinstance(fpath, type(u'')):
        fpath = fpath.encode('iso8859-1', 'replace')

    return extinf + fpath + '\n'
    
def doDir(d):
    ''' Called recursively for each directory in the tree.
    '''

    if d != '.':
        safeprint('%s...' % d)

    # Make a new .m3u file for this directory.
    m3u = open(d / (d.abspath().name + '.m3u'), 'w')
    m3u.write('#EXTM3U\n')
    m3us.append(m3u)

    # Add all the .mp3's in this dir to all the .m3u's.
    for f in d.files('*.mp3'):
        m3ustring = getM3uString(f)        
        for m3ufile in m3us:
            m3ufile.write(m3ustring)

    # Recurse into all the subdirectories.
    for dchild in d.dirs():
        doDir(dchild)
    
    # We're done with this directory's .m3u file.
    m3us.pop()

if __name__ == '__main__':
    doDir(path.path('.'))

# History:
# 20040104  Created
# 20040106  Protect mp3.py calls to catch and print exceptions.
# 20040109  Don't write an EXTINF line if there is nothing interesting to write.
#           Protect against exceptions in id3reader.
# 20040110  Deal with Unicode paths properly.
# 20040113  All printing goes through a helper to get Unicode right.
#           Don't write an EXTINF line if there is no caption.
