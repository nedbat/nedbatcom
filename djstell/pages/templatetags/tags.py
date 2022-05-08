import datetime
import functools
import hashlib
import os.path
import re

from django.conf import settings
from django.template import Library, Node
from django.template.defaultfilters import stringfilter
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from djstell.pages.models import Entry, Tag, Link
from djstell.pages.sitemap import SiteMap

register = Library()

@register.inclusion_tag('entry.html')
def blog_entry(entry, mode):
    return {'entry':entry, 'mode':mode, 'settings': settings}

@register.inclusion_tag('sidebar.html')
def sidebar(which):
    """ Make the sidebar.
    """
    c = {}
    c['which'] = which

    more_blog = combined_more_blog()

    if which == 'blog':
        c['moreblog'] = more_blog
        c['morebloglabel'] = "More blog"
        c['staycurrent'] = True
    elif which == 'page':
        c['moreblog'] = more_blog[:22]
        c['morebloglabel'] = "Blog"

    return c

@register.inclusion_tag('navbar.html')
def navbar():
    """ Make the navbar.
    """
    return {}

@register.inclusion_tag('metatags.html')
def metatags():
    """ Make the meta tags.
    """
    return {}


@functools.cache
def combined_more_blog():
    return list(_combined_more_blog())

def _combined_more_blog():
    """Yield a sequence of shuffled-together tags and years."""
    avoid_tags = ('me', 'site', 'blogs')
    tags = Tag.objects.all().exclude(tag__in=avoid_tags)
    sunset = datetime.datetime.now() - datetime.timedelta(days=5*365)
    tags = sorted(
        tags,
        key=lambda t: t.entry_set_no_drafts().filter(when__gt=sunset).count(),
        reverse=True
    )
    tags = ({'link': t.permaurl(), 'text': t.short or t.name} for t in tags)
    tags = iter(tags)

    years = ( d.year for d in Entry.objects.dates('when', 'year', order='DESC') )
    years = ({'link': f'/blog/archive/year{y}.html', 'text': f"'{y % 100:02d}"} for y in years)
    years = iter(years)

    # Interleave tags and years.
    try:
        while True:
            yield next(tags)
            yield next(tags)
            yield next(years)
            yield next(tags)
            yield next(years)
    except StopIteration:   # ran out of years..
        pass

    # Then some more tags
    for _ in range(8):
        yield next(tags)

@register.simple_tag
def year_range(year1, year2):
    """ Return a range of years, if the two years are different.
    """
    if hasattr(year1, 'year'):
        year1 = year1.year
    if hasattr(year2, 'year'):
        year2 = year2.year
    if year1 == year2:
        return str(year1)
    else:
        return format_html(mark_safe("{}&ndash;{}"), year1, year2)

special_ch = {
    '':     '',
    '_':    '&#x20;',       #    plain-old space, to protect from spaceless
    '>>':   '&#xbb;',       # »  RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    '<<':   '&#xab;',       # «  LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    '(c)':  '&#xa9;',       # ©  COPYRIGHT SIGN
    'S':    '&#xa7;',       # §  SECTION SIGN
    '*':    '&#x2022;',     # •  BULLET
    '.':    '&#xb7;',       # ·  MIDDLE DOT
    ':':    '&#xb7;&#xb7;', #    two middle dots, a strange colon-like thing
    '-':    '&#x2013;',     # –  EN DASH
    '--':   '&#x2014;',     # —  EM DASH
    ':>':   '&#x25b6;',     # ▶  BLACK RIGHT-POINTING TRIANGLE
    'o':    '&#x25e6;',     # ◦  WHITE BULLET
    '[]':   '&#x25ab;',     # ▫  WHITE SMALL SQUARE
    '<>':   '&#x25c7;',     # ◇  WHITE DIAMOND
    }

@register.simple_tag
def ch(value):
    return mark_safe('&#xa0;'.join([special_ch[s] for s in value.split(' ')]))

@register.simple_tag
def twodigit(value):
    """Show just the last two digits of a number (ex: a year)"""
    return str(value)[-2:]

STATIC_PATH = [settings.STATIC_ROOT, "."]

@register.simple_tag
def static_link(filename):
    """Insert our best cache-busting static link."""
    main, ext = os.path.splitext(filename)
    if settings.DEPLOY_TIME:
        # On real servers, add a hash to the url, to bust caches.
        for static_dir in STATIC_PATH:
            static_file = os.path.join(static_dir, filename)
            if os.path.exists(static_file):
                with open(static_file, "rb") as fstatic:
                    md5 = hashlib.md5(fstatic.read()).hexdigest()[:12]
                main = f"{main}__{md5}"
                break
    base = settings.BASE
    if settings.STATIC_URL:
        base += settings.STATIC_URL.rstrip("/")
    url = f"{base}/{main}{ext}"
    if ext == ".css":
        tag = f"<link rel='stylesheet' href='{url}' type='text/css'>"
    elif ext == ".js":
        tag = f"<script type='text/javascript' src='{url}'></script>"
    return mark_safe(tag)

@register.simple_tag
def static_url_link(url, type, defer=False):
    """Reference third-party static stuff in the best way."""
    if type == 'css':
        if defer:
            # https://web.dev/defer-non-critical-css/
            tag = (
                f'''<link rel="preload" href="{url}" as="style" onload="this.onload=null;this.rel='stylesheet'">'''
                f'''<noscript><link href="{url}" rel="stylesheet"></noscript>'''
            )
        else:
            tag = f'<link href="{url}" rel="stylesheet">'
    elif type == 'js':
        if defer:
            tag = f'<script src="{url}" async="async"></script>'
        else:
            tag = f'<script src="{url}"></script>'
    else:
        raise Exception(f"Don't know static_url_link type: {type!r}")
    return mark_safe(tag)

@register.tag
def ifnotfirst(parser, token):
    """Like ``{% if not forloop.first %}`` but a little different.

    forloop.first is true only for the first iteration of a loop.
    This is true for the second and subsequent times the tag is
    encountered.  This can be different if inside a conditional.
    """
    bits = token.contents.split()
    nodelist = parser.parse(('endifnotfirst',))
    parser.delete_first_token()
    return IfNotFirstNode(nodelist, *bits[1:])

class IfNotFirstNode(Node):
    def __init__(self, nodelist, *varlist):
        self.nodelist = nodelist
        self._checked = False

    def render(self, context):
        if 'forloop' in context and '_iffirst' not in context['forloop']:
            self._checked = False
            context['forloop']['_iffirst'] = True

        if self._checked:
            content = self.nodelist.render(context)
        else:
            content = ''

        self._checked = True
        return content

@register.simple_tag
@functools.cache
def top_areas():
    crumbs = SiteMap().top_areas()
    links = [ "<a href='%s'>%s</a>" % (href, title) for (title, href) in crumbs ]
    return mark_safe(u" \N{MIDDLE DOT} ".join(links))

@register.filter()
@stringfilter
def first_sentence(value, number=1):
    from djstell.pages.text import first_sentence
    return first_sentence(value, number)

@register.filter()
@stringfilter
def widont(value):
    """ Join the last two words with an &nbsp; to prevent widowed words.
    """
    word = ''
    while value:
        value, end = value.rsplit(" ", 1)
        if word:
            word = end + ' ' + word
        else:
            word = end
        if word.count('<') == word.count('>'):
            break
    if value:
        return value + "&#xa0;" + word
    else:
        return word

@register.filter()
@stringfilter
def nbsp(value):
    """Change all spaces to &nbsp;. Only use on html-safe stuff."""
    return mark_safe(value.replace(" ", "&#xa0;"))

@register.filter()
@stringfilter
def just_text(value):
    from djstell.pages.text import just_text
    return just_text(value)

from django.template.defaulttags import SpacelessNode as ReallySpacelessNode

@register.tag
def reallyspaceless(parser, token):
    nodelist = parser.parse(('endreallyspaceless',))
    parser.delete_first_token()
    return ReallySpacelessNode(nodelist)

# Our own spaceless that works the way I want.
@register.tag
def spaceless(parser, token):
    nodelist = parser.parse(('endspaceless',))
    parser.delete_first_token()
    return SpacelessNode(nodelist)

class SpacelessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        s = self.nodelist.render(context).strip()
        inline_tags = 'a|b|i|u|em|strong|sup|sub|tt|font|small|big|input|span'
        inlines_with_spaces = r'</(%s)>\s+<(%s)\b' % (inline_tags, inline_tags)
        s = re.sub(inlines_with_spaces, r'</\1>&#preservespace;<\2', s)
        s = re.sub(r'<(\w+)([^>]+)>\s+</\1>', r'<\1\2>&#preservespace;</\1>', s)
        s = re.sub(r'>\s+<', '><', s)
        s = s.replace('&#preservespace;', ' ')
        return s
