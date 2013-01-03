""" Print all the files in a set of VC++.net projects.
    Ned Batchelder, July 2003
    http://www.nedbatchelder.com
"""

import path, sys
from xml.dom import Node
from xml.dom.ext.reader import PyExpat
import StringIO

class XmlParse:
    """A simple wrapper around the PyExpat XML parser."""
    def __init__(self, uri):
        try:
            xmlstr = open(uri, 'r').read()
            # PyExpat can't handle Windows-1252, but it's all ASCII anyway,
            # so claim utf-8.
            xmlstr = xmlstr.replace('encoding = "Windows-1252"', 'encoding="UTF-8"')
            xmlstm = StringIO.StringIO(xmlstr)
            self.reader = PyExpat.Reader()
            self.doc = self.reader.fromStream(xmlstm)
            self.documentElement = self.doc.documentElement
        except ExpatError, msg:
            raise "XML error: %s in %s" % (msg, uri)
            
    def release(self):
        self.reader.releaseNode(self.doc)
        
class ProjectFileParser:
    """Find and harvest files from all .vcproj files"""
    def __init__(self, filePath, fileDict, exts=[]):
        self.filePath = filePath
        self.baseDir = self.filePath.parent
        self.fileDict = fileDict
        self.exts = exts

    def parse(self):
        """Parse the vcproj file"""
        xml = XmlParse(self.filePath)
        self.doElement(xml.documentElement)
        xml.release()

    def doElement(self, e):
        if e.localName == 'File':
            relpath = path.path(e.getAttribute('RelativePath'))
            if not self.exts or (relpath.ext in self.exts):
                abs = (self.baseDir / relpath).abspath()
                self.fileDict[abs] = 0
        else:
            for eChild in e.childNodes:
                if eChild.nodeType == Node.ELEMENT_NODE:
                    self.doElement(eChild)

# Main

projectfiles = {}
dir = path.path('.')
for f in dir.walkfiles('*.vcproj'):
    pfp = ProjectFileParser(f, projectfiles, sys.argv[1:])
    pfp.parse()

files = projectfiles.keys()
files.sort()
for f in files:
    print f
