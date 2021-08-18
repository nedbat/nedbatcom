# Make a site!

import collections
import datetime

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext, Template

from djstell.pages.models import Entry, Article, Tag
from djstell.pages.templatetags.tags import first_sentence, just_text
from djstell.pages.text import description_safe

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
    c['description'] = description_safe(ent.description or first_sentence(just_text(ent.to_html()), 2))
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
    return render(request, 'oneentry.html', c)

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
    tags = Tag.objects.all().order_by('name')
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

def blog_moved_php(request):
    ents = Entry.objects.all()
    # Only need to include entries with a <more> tag, and before the re-implementation.
    ents = [ e for e in ents if ("<more" in e.text) and (e.when.year < 2008) ]

    c = {}
    c['entries'] = ents
    return render(request, 'moved.php', c)

## Article stuff

def article_root(request, path):
    return article(request, f"{path}/index.html")

def article(request, path):
    pxpath = path.replace('.html', '.px')
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
    c['body'] = a.to_html()
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
    return render(request, 'article.html', c)

def sidebar(request, which):
    html = "{% load tags %}{% sidebar which 1 %}"
    c = RequestContext(request)
    c['which'] = which
    return HttpResponse(Template(html).render(c))

def navbar(request):
    html = "{% load tags %}{% navbar 1 %}"
    return HttpResponse(Template(html).render(RequestContext(request)))

def metatags(request):
    html = "{% load tags %}{% metatags 1 %}"
    return HttpResponse(Template(html).render(RequestContext(request)))

def index(request):
    a = get_object_or_404(Article, path='index.px')
    c = {}
    c['title'] = a.title
    c['body'] = a.to_html()
    c['recent_entries'] = list(Entry.objects.all().order_by('-when')[:6])
    now = datetime.datetime.now()
    for recent in c['recent_entries']:
        recent.show_year = (now - recent.when).days > 60

    # Tags to display: the most populated ones, but not "me", "site", etc.
    # Only include tags from the last few years.
    num_to_display = 28
    years = 5
    bad_tags = {'me', 'site', 'mycode'}
    sunset = datetime.datetime.now() - datetime.timedelta(days=years*365)
    entries = list(Entry.objects.filter(when__gt=sunset))
    census = collections.Counter()
    for entry in entries:
        for tag in entry.tags.all():
            if tag.tag not in bad_tags:
                census[tag] += 1
    tags = [t[0] for t in census.most_common(num_to_display)]
    tags = sorted(tags, key=lambda t: t.name)
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
