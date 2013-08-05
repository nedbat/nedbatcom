# Extensions.
from lxml import etree
from stellated.XsltExtensions import *
from cStringIO import StringIO
from django.conf import settings
#import re, smartypants

#smartypants.tags_to_skip_regex = re.compile("<(/)?(?:pre|code|kbd|script|math|tt)[^>]*>")

def wrapit(fn):
    """ lxml extensions have a first dummy arg that Pyana extensions don't.  Adapt.
    """
    def inside(dummy, *args):
        try:
            return fn(*args)
        except Exception, e:
            print "Error in XSLT extension: %s" % e
            raise
    return inside

ns = etree.FunctionNamespace('http://www.stellated.com/xuff')
ns['endswith'] = wrapit(endswith)
ns['makeuri'] = wrapit(makeuri)
ns['urlquote'] = wrapit(urlquote)
ns['phpquote'] = wrapit(phpquote)
ns['now'] = wrapit(now8601)
ns['w3cdtf'] = wrapit(w3cdtf)
ns['idfromtext'] = wrapit(idfromtext)
ns['slugfromtext'] = wrapit(slugfromtext)
ns['lexcode'] = wrapit(lexcode)
ns['imgwidth'] = wrapit(imgwidth)
ns['imgheight'] = wrapit(imgheight)

def pathtitle(path):
    """ Return the title of a page at a given path.
    """
    from djstell.pages.models import Article
    art = Article.objects.get(path=path[0])
    return art.title

ns['pathtitle'] = wrapit(pathtitle)

# The transform from xml to html for content.
xslt = etree.parse(r'c:\ned\web\stellated\content.xslt')
xslt_xform = etree.XSLT(xslt)

def content_transform(name, xmltext, child=None, params={}):
    #print "XSLT: %.80s(%s) %r" % (xmltext.replace('\n', ' '), child or '-', params.get('blogmode', ''))
    f = StringIO(xmltext.encode('utf-8'))
    doc = etree.parse(f)
    if child:
        doc = doc.find(child)
    params = dict(params)
    params.update({
        'base':     string_param(settings.BASE),
        })
    html = str(xslt_xform(doc, **params))
    #html = smartypants.smartyPants(html, 'q')
    for entry in xslt_xform.error_log:
        if entry.filename == '<string>':
            fname = name
        else:
            fname = entry.filename
        print "Message, %s @ %d: %s" % (fname, entry.line, entry.message)
    return html

def string_param(s):
    # Convert the string to an XSLT string literal.  There's no escaping of characters
    # in XPath string literals, so we have to break strings if they have both
    # single- and double-quotes.
    #
    # The string:
    #   What's a "blog"?
    # comes out as:
    #   "What's a "+'"'+"blog"+'"'+"?"
    parts = s.split('"')
    return "+'\"'+".join([ repr(unicode(p).encode('utf-8')) for p in parts ])
