# Create your views here.

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Template

from djstell.pages.models import Entry, Article, Tag

## Blog stuff

blog_crumbs = [('Home', '/'), ('Blog', '/blog')]

def add_entries(c, ents):
    ents = list(ents)
    c['entries'] = ents
    if ents:
        c['min_date'] = ents[-1].when
        c['max_date'] = ents[0].when
    c['crumbs'] = blog_crumbs

def abs_url(url):
    absurl = settings.BASE
    if not absurl.endswith('/') and not url.startswith('/'):
        absurl += '/'
    absurl += url
    return absurl

def entry(request, year, month, slug):
    """ Single entry.
    """
    ent = get_object_or_404(Entry.objects.select_related(), when__year=int(year), when__month=int(month), slug=slug)
    c = RequestContext(request)
    c['entry'] = ent
    c['title'] = ent.title
    c['min_date'] = c['max_date'] = ent.when
    c['crumbs'] = blog_crumbs + [(ent.when.strftime("%B %Y"), ent.monthurl())]
    c['comments'] = {
        'entryid': ent.entryid(),
        'url': abs_url(ent.permaurl()),
        'title': ent.title,
        'closed': ent.comments_closed,
        }
    return render_to_response('oneentry.html', c)

def blogmain(request):
    """ The main blog page. A dozen recent entries.
    """
    ents = list(Entry.objects.all().order_by('-when')[:25])
    c = RequestContext(request)
    add_entries(c, ents)
    c['title'] = 'Blog'
    c['crumbs'] = c['crumbs'][:1]
    return render_to_response('blogmain.html', c)

def month(request, year, month):
    """ A monthly blog page.
    """
    ents = list(Entry.objects.filter(when__year=int(year), when__month=int(month)).order_by('-when'))
    if not ents:
        raise Http404

    c = RequestContext(request)
    add_entries(c, ents)
    c['title'] = ents[0].when.strftime("%B %Y")     # October 2007

    # next and prev
    c['prev_ent'] = c['next_ent'] = None
    prev = Entry.objects.filter(when__lt=ents[-1].when).order_by('-when')[:1]
    if prev:
        c['prev_ent'] = prev[0]
    next = Entry.objects.filter(when__gt=ents[0].when).order_by('when')[:1]
    if next:
        c['next_ent'] = next[0]

    return render_to_response('blogmonth.html', c)

def archiveyear(request, year):
    ents = list(Entry.objects.filter(when__year=int(year)).order_by('-when'))
    c = RequestContext(request)
    add_entries(c, ents)
    c['type'] = 'year'
    c['year'] = year
    c['title'] = "Blog Archive: %s" % year
    return render_to_response('blogarchive.html', c)

def archiveall(request):
    ents = list(Entry.objects.all().order_by('-when'))
    c = RequestContext(request)
    add_entries(c, ents)
    c['type'] = 'complete'
    c['title'] = "Blog Archive: Complete"
    return render_to_response('blogarchive.html', c)

def tags(request):
    tags = Tag.objects.all().order_by('name')
    c = RequestContext(request)
    c['tags'] = tags
    c['min_date'] = Entry.objects.all().order_by('when')[0].when
    c['max_date'] = Entry.objects.all().order_by('-when')[0].when
    c['untagged'] = untagged_entries()
    c['title'] = 'Blog post tags'
    c['crumbs'] = blog_crumbs
    return render_to_response('alltags.html', c)

def tag(request, slug):
    tag = Tag.objects.get(tag=slug)
    ents = tag.entry_set.filter(draft=False).order_by('-when')
    c = RequestContext(request)
    add_entries(c, ents)
    c['tag'] = tag
    c['title'] = 'Tag: %s' % tag.name
    c['crumbs'] = blog_crumbs + [('Tags', '/blog/tags.html')]
    return render_to_response('tags.html', c)

def untagged(request):
    ents = untagged_entries()
    c = RequestContext(request)
    add_entries(c, ents)
    c['title'] = 'Untagged posts'
    c['crumbs'] = blog_crumbs + [('Tags', 'blog/tags.html')]
    return render_to_response('tags.html', c)

def untagged_entries():
    # There's probably a good ORM way to find untagged entries, but I don't know what it is.
    ents = Entry.objects.all().order_by('-when')
    ents = [e for e in ents if e.tags.all().count() == 0]
    return ents

def blog_rss(request):
    """The RSS feed for the whole blog."""
    ents = Entry.objects.all().order_by('-when')[:10]
    c = RequestContext(request)
    c['entries'] = ents
    return render_to_response('rss.xml', c)

def tags_rss(request, tags):
    """An RSS feed for just the tags mentioned in `tags`."""
    c = RequestContext(request)
    c['entries'] = Entry.objects.filter(tags__tag__in=tags).distinct().order_by('-when')[:10]
    return render_to_response('rss.xml', c)

def blog_moved_php(request):
    ents = Entry.objects.all()
    # Only need to include entries with a <more> tag, and before the re-implementation.
    ents = [ e for e in ents if ("<more" in e.text) and (e.when.year < 2008) ]

    c = RequestContext(request)
    c['entries'] = ents
    return render_to_response('moved.php', c)

## Article stuff

def article(request, path):
    pxpath = path.replace('.html', '.px')
    a = get_object_or_404(Article, path=pxpath)
    c = RequestContext(request)
    c['title'] = a.title
    c['lang'] = a.lang
    c['copyright'] = a.copyright
    c['meta'] = a.meta
    edits = list(a.whatwhen_set.all().order_by('when'))
    if edits:
        c['min_date'] = edits[0].when
        c['max_date'] = edits[-1].when
    c['body'] = a.to_html()
    c['crumbs'] = a.breadcrumbs()
    if a.comments:
        c['comments'] = {'entryid':path, 'url':abs_url(path), 'title':a.title}
    return render_to_response('page.html', c)

def sidebar(request, which):
    html = "{% load tags %}{% sidebar which 1 %}"
    c = RequestContext(request)
    c['which'] = which
    return HttpResponse(Template(html).render(c))

def index(request):
    a = get_object_or_404(Article, path='index.px')
    c = RequestContext(request)
    c['title'] = a.title
    c['body'] = a.to_html()
    c['recent_entries'] = list(Entry.objects.all().order_by('-when')[:6])

    # Tags to display: the most populated ones, but not "me", "site", etc.
    bad_tags = ('me', 'site', 'mycode')
    tags = Tag.objects.all().exclude(tag__in=bad_tags)
    tags = sorted(tags, key=lambda t: t.entry_set.count(), reverse=True)
    tags = tags[:28]
    tags = sorted(tags, key=lambda t: t.name)
    c['tags'] = tags

    # Blog info
    c['archive_years'] = [ d.year for d in Entry.objects.dates('when', 'year', order='DESC') ]

    title, url, description = 'title', 'url', 'description'
    # Code
    c['code'] = [
        { title: 'Aptus', url: 'code/aptus', description: 'a Mandelbrot set explorer' },
        { title: 'coverage.py', url: 'code/coverage', description: 'for measuring Python code coverage' },
        { title: 'hyphenate', url: 'code/modules/hyphenate.html', description: 'for hyphenating words with the Liang/Knuth algorithm' },
    ]

    # Text
    c['text'] = [
        { title: 'Pragmatic Unicode', url: 'text/unipain.html', description: 'how to stop the pain' },
        { title: 'Stopping spambots with hashes and honeypots', url: 'text/stopbots.html', description: 'no more CAPTCHAs' },
        #{ title: 'Exceptions in the rainforest', url: 'text/exceptions-in-the-rainforest.html', description: 'where throw and catch fit it' },
        { title: 'A good thing about autism', url: 'text/autism-examined.html', description: 'a view from the trenches' },
    ]

    return render_to_response('mainpage.html', c)
