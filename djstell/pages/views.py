# Make a site!

import collections
import datetime
import logging
import os
import os.path
import time

import bleach
import bleach.css_sanitizer
from django.conf import settings
from django.db.models.functions import Lower
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext, Template
from django.views.decorators.cache import patch_cache_control
from django.views.static import serve as serve_static
from django_sendfile import sendfile

from djstell.pages.models import Entry, Article, Tag

logger = logging.getLogger(__name__)

## Blog stuff

def add_entries(c, ents):
    ents = list(ents)
    c['entries'] = ents
    if ents:
        c['min_date'] = ents[-1].when
        c['max_date'] = ents[0].when

def abs_url(url):
    if not url:
        return url
    absurl = settings.EXT_BASE
    if not absurl.endswith('/') and not url.startswith('/'):
        absurl += '/'
    absurl += url
    return absurl

def render_or_redirect(request, template, c, obj):
    """For views which might post comments: render or redirect."""
    # Kind of a gross hack: processing the post is done deep in the
    # honey templatetag.  We put a mutable list in the context so
    # that the templatetag can send data back about whether to redirect
    # (if the post was finished) or not (if the post was not).
    c['should_redirect'] = [False]
    resp = render(request, template, c)
    if c['should_redirect'][0]:
        resp = redirect(obj.permaurl())
    else:
        # There's only one logged-in user, so we can just switch the cache based
        # on is_anonymous or not.
        patch_cache_control(resp, public=request.user.is_anonymous)
    return resp

def entry(request, year, month, slug):
    """ Single entry.
    """
    ent = get_object_or_404(Entry.all_entries.select_related(), when__year=int(year), when__month=int(month), slug=slug)
    c = {}
    c['entry'] = ent
    c['title'] = ent.title
    c['url'] = abs_url(ent.permaurl())
    c['features'] = ent.features.split(';')
    c['bodyclass'] = 'blog oneentry'
    c['min_date'] = c['max_date'] = ent.when
    c['description'] = ent.ogdescription()
    c['image'] = abs_url(ent.image)
    c['image_alt'] = ent.image_alt
    if ent.draft:
        c['comments'] = None
    else:
        c['comments'] = {
            'entryid': ent.entryid(),
            'url': abs_url(ent.permaurl()),
            'title': ent.title,
            'closed': ent.comments_closed,
            }
    return render_or_redirect(request, 'oneentry.html', c, ent)

def entry_by_date(request, whenid):
    when = datetime.datetime(*time.strptime(whenid, "%Y%m%dT%H%M%S")[:6])
    ent = get_object_or_404(Entry.all_entries.select_related(), when=when)
    return redirect(ent.permaurl())

def blogmain(request):
    """ The main blog page. A dozen recent entries.
    """
    ents = list(Entry.objects.all().order_by('-when')[:12])
    c = {}
    add_entries(c, ents)
    c['entries_shown'] = shown = ents[:6]
    features = set()
    for ent in shown:
        features.update(ent.features.split(';'))
    c['features'] = features
    c['entries_listed'] = ents[6:]
    c['title'] = 'Blog'
    c['hide_h1'] = True
    c['bodyclass'] = 'blog main'
    return render(request, 'blogmain.html', c)

def archiveyear(request, year):
    ents = list(Entry.objects.filter(when__year=int(year)).order_by('-when'))
    c = {}
    add_entries(c, ents)
    c['type'] = 'year'
    c['year'] = year
    c['title'] = 'Blog: %s' % year
    c['bodyclass'] = 'blog archive year'
    return render(request, 'blogarchive.html', c)

def archivedate(request, month, day):
    date = datetime.datetime(2004, int(month), int(day))
    ents = list(Entry.objects.filter(when__month=date.month, when__day=date.day).order_by('-when'))
    c = {}
    add_entries(c, ents)
    c['type'] = 'date'
    c['date'] = date
    c['title'] = date.strftime('Blog: %B %-d')
    c['bodyclass'] = 'blog archive date'
    c['prev_date'] = date - datetime.timedelta(days=1)
    c['next_date'] = date + datetime.timedelta(days=1)
    return render(request, 'blogarchive.html', c)

def archiveall(request):
    ents = list(Entry.objects.all().order_by('-when'))
    c = {}
    add_entries(c, ents)
    c['type'] = 'complete'
    c['title'] = 'Blog: Complete'
    c['bodyclass'] = 'blog archive all'
    return render(request, 'blogarchive.html', c)

def tags(request):
    tags = Tag.objects.all().order_by(Lower('name'))
    c = {}
    c['tags'] = tags
    c['min_date'] = Entry.objects.all().order_by('when')[0].when
    c['max_date'] = Entry.objects.all().order_by('-when')[0].when
    c['untagged'] = untagged_entries()
    c['title'] = 'Blog: tags'
    c['bodyclass'] = 'blog tags'
    return render(request, 'alltags.html', c)

def tag(request, slug):
    tag = Tag.objects.get(tag=slug)
    ents = tag.entry_set_no_drafts().order_by('-when')
    c = {}
    add_entries(c, ents)
    c['tag'] = tag
    c['title'] = 'Blog: #%s' % tag.hashtag
    c['bodyclass'] = 'blog tag'
    return render(request, 'tags.html', c)

def untagged(request):
    ents = untagged_entries()
    c = {}
    add_entries(c, ents)
    c['title'] = 'Blog: untagged'
    c['bodyclass'] = 'blog tag'
    return render(request, 'tags.html', c)

def untagged_entries():
    # There's probably a good ORM way to find untagged entries, but I don't know what it is.
    ents = Entry.objects.all().order_by('-when')
    ents = [e for e in ents if e.tags.all().count() == 0]
    return ents

def drafts(request):
    ents = list(Entry.drafts.all().order_by('-when'))
    c = {}
    add_entries(c, ents)
    c['type'] = 'drafts'
    c['title'] = 'Blog: Drafts'
    c['bodyclass'] = 'blog archive all'
    return render(request, 'blogarchive.html', c)

def blog_rss(request):
    """The RSS feed for the whole blog."""
    ents = Entry.objects.all().order_by('-when')[:10]
    c = {}
    c['entries'] = ents
    return render(request, 'rss.xml', c)

def tags_rss(request, tags):
    """An RSS feed for just the tags mentioned in `tags`."""
    c = {}
    c['entries'] = Entry.objects.filter(tags__tag__in=tags).distinct().order_by('-when')[:10]
    return render(request, 'rss.xml', c)

## Article stuff

def article(request, path):
    if settings.STATIC_ROOT:
        maybe_file = os.path.join(settings.STATIC_ROOT, path)
        if os.path.exists(maybe_file) and not os.path.isdir(maybe_file):
            return sendfile(request, os.path.abspath(maybe_file))

    if path.endswith(".html"):
        pxpath = path.replace('.html', '.px')
    else:
        pxpath = path.rstrip("/") + "/index.px"
    a = get_object_or_404(Article, path=pxpath)
    c = {}
    c['title'] = a.title
    c['url'] = abs_url(a.permaurl())
    c['lang'] = a.lang
    c['copyright'] = a.copyright
    c['meta'] = a.meta
    c['scripts'] = a.scripts.split()
    c['style'] = a.style
    c['features'] = a.features
    edits = list(a.whatwhen_set.all().order_by('when'))
    if edits:
        c['min_date'] = edits[0].when
        c['max_date'] = edits[-1].when
    c['pagebody'] = a.to_html()
    c['description'] = a.description
    c['image'] = abs_url(a.image)
    c['image_alt'] = a.image_alt
    if a.comments:
        c['comments'] = {
            'entryid': path,
            'url': abs_url(path),
            'title': a.title,
            'lorem': path == "text/lorem.html",
        }
    return render_or_redirect(request, 'article.html', c, a)

def index(request):
    num_entries = 4
    num_tags = 25
    tag_years = 3
    bad_tags = {"me", "site", "mycode"}

    a = get_object_or_404(Article, path='index.px')
    c = {}
    c['title'] = a.title
    c['pagebody'] = a.to_html()
    c['recent_entries'] = list(Entry.objects.all().order_by('-when')[:num_entries])
    now = datetime.datetime.now()
    for recent in c['recent_entries']:
        recent.show_year = (now - recent.when).days > 60

    # Tags to display: the most populated ones, but not "me", "site", etc, and
    # only include tags from the last few years.
    sunset = datetime.datetime.now() - datetime.timedelta(days=tag_years*365)
    census = collections.Counter()
    for entry in Entry.objects.filter(when__gt=sunset):
        for tag in entry.tags.all():
            if tag.tag not in bad_tags:
                census[tag] += 1
    tags = [t[0] for t in census.most_common(num_tags)]
    tags = sorted(tags, key=lambda t: t.hashtag)
    c['tags'] = tags

    # Blog info
    c['archive_years'] = [ d.year for d in Entry.objects.dates('when', 'year', order='DESC') ]

    title, url, description = 'title', 'url', 'description'
    # Code
    c['code'] = [
        { title: 'Flourish', url: 'blog/202101/flourish.html', description: 'a harmonograph explorer' },
        { title: 'coverage.py', url: 'code/coverage', description: 'for measuring Python code coverage' },
        { title: 'Scriv', url: 'blog/202009/scriv.html', description: 'for managing changelogs' },
    ]

    # Text
    c['text'] = [
        { title: 'Python Names and Values', url: 'text/names1.html', description: 'how assignment works' },
        { title: 'Kindling projects', url: 'text/kindling.html', description: 'small projects for new programmers' },
        { title: 'Pragmatic Unicode', url: 'text/unipain.html', description: 'how to stop the pain' },
    ]

    return render(request, 'mainpage.html', c)


def summary(request):
    entries = list(Entry.objects.all().order_by('-when')[:10])
    cleaner = bleach.sanitizer.Cleaner(
        tags=[],
        strip=True,
        strip_comments=True,
        css_sanitizer=bleach.css_sanitizer.CSSSanitizer(allowed_css_properties=[])
    )
    resp = {}
    resp["entries"] = [
        {
            "title": e.title,
            "when_iso": e.when.strftime("%Y%m%d"),
            "description": e.ogdescription(),
            "description_text": cleaner.clean(e.ogdescription()).strip(),
            "url": settings.EXT_BASE + e.permaurl(),
        }
        for e in entries
    ]
    return JsonResponse(resp, json_dumps_params=dict(indent=4))


def crash(request):
    logger.warning("About to crash")
    print("stdout: about to crash")
    raise Exception("Crash requested")


DOCROOT = "public"

def last_resort(request, path):
    """Handle some things .htaccess used to do for us."""
    # Serve index.html for directories in the document root.
    fpath = os.path.join(DOCROOT, path)
    if os.path.isdir(fpath):
        index = os.path.join(fpath, "index.html")
        if os.path.exists(index):
            new = path + "/"
            if not path.startswith("/"):
                new = "/" + new
            return redirect(new)

    # Serve static files.
    if settings.STATIC_URL:
        return serve_static(request, path=path, document_root=settings.MY_BOGUS_STATIC_DIR)
    else:
        raise Http404(f"Couldn't find {path=}")


def not_found(request, *args, **kwargs):
    """The view function for 404's"""
    resp = article(request, path="err404.html")
    resp.status_code = 404
    return resp
