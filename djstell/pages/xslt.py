# Extensions.

from io import BytesIO
import re

from lxml import etree
from stellated.XsltExtensions import *
from django.conf import settings
import smartypants


def wrapit(fn):
    """ lxml extensions have a first dummy arg that Pyana extensions don't.  Adapt.
    """
    def inside(dummy, *args):
        try:
            return fn(*args)
        except Exception as e:
            print("Error in XSLT extension: %s" % e)
            raise
    return inside

ns = etree.FunctionNamespace('http://www.stellated.com/xuff')
ns['makeuri'] = wrapit(makeuri)
ns['now'] = wrapit(now8601)
ns['idfromtext'] = wrapit(idfromtext)
ns['lexcode'] = wrapit(lexcode)
ns['imgwidth'] = wrapit(imgwidth)
ns['imgheight'] = wrapit(imgheight)

#ns['endswith'] = wrapit(endswith)
#ns['urlquote'] = wrapit(urlquote)
#ns['phpquote'] = wrapit(phpquote)
#ns['w3cdtf'] = wrapit(w3cdtf)
#ns['slugfromtext'] = wrapit(slugfromtext)
#ns['smartypants'] = wrapit(smartypants.smartypants)

def thing_from_path(path):
    from djstell.pages.models import Article, Entry
    try:
        thing = Article.objects.get(path=path[0])
    except Article.DoesNotExist:
        try:
            thing = Entry.all_entries.get(path=path[0])
        except Entry.DoesNotExist:
            # $set_env.py: STELL_MISSING_OK - Don't complain if a pref is missing.
            if os.environ.get("STELL_MISSING_OK", ""):
                class Fake(object):
                    def __init__(self):
                        self.title = "MISSING PAGE"
                    def permaurl(self):
                        return "/text/missing.html"
                return Fake()
            else:
                raise Exception(f"Couldn't find thing_from_path({path=})")
    return thing

def pathtitle(path):
    """ Return the title of a page at a given path.
    """
    return thing_from_path(path).title

ns['pathtitle'] = wrapit(pathtitle)

def permaurl(path):
    try:
        return thing_from_path(path).permaurl()
    except Exception as exc:
        print("Couldn't get permaurl({!r}): {}".format(path, exc))
        raise

ns['permaurl'] = wrapit(permaurl)

# The transform from xml to html for content.
XSLT_XFORM = None

def content_transform(name, xmltext, child=None, params={}):
    #print("XSLT: %.80s(%s) %r" % (xmltext.replace('\n', ' '), child or '-', params.get('blogmode', '')))
    global XSLT_XFORM
    if XSLT_XFORM is None:
        XSLT_XFORM = etree.XSLT(etree.parse("content.xslt"))

    f = BytesIO(xmltext.encode('utf-8'))
    try:
        doc = etree.parse(f)
    except:
        print("Text was {!r}".format(xmltext))
        raise
    if child:
        doc = doc.find(child)
    params = dict(params)
    params.update({
        'base':     string_param(settings.BASE),
        })
    html = str(XSLT_XFORM(doc, **params))
    # smartypants doesn't handle </a>' properly.
    html = re.sub(r"(</\w+>)'", r"\1&#8217;", html)
    html = smartypants.smartypants(html, smartypants.Attr.q | smartypants.Attr.n)
    #print("Transformed {!r} into {!r}".format(xmltext[:80], html[:80]))
    for entry in XSLT_XFORM.error_log:
        if entry.filename == '<string>':
            fname = name
        else:
            fname = entry.filename
        print("Message, %s @ %d: %s" % (fname, entry.line, entry.message))
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
    return "+'\"'+".join([ repr(str(p).encode('utf-8'))[1:] for p in parts ])
