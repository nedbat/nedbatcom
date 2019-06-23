# nedbatchelder.com models

import datetime
import re
import time

from .util import *
from .xslt import content_transform, string_param

from django.db import models
from lxml import etree
import smartypants

if 0:
    f_plain_text = open("all-site.txt", "w")

    def save_plain_text(elt):
        for xpath in ["p", "ul/li"]:
            for p in elt.findall(xpath):
                if p.text:
                    f_plain_text.write(p.text.encode('utf-8'))
                    f_plain_text.write("\n\n")

else:
    def save_plain_text(elt):
        return


def nice_text(s):
    """Make the text nice, with curly quotes and whatnot.

    Takes unicode, returns unicode.
    """
    return smartypants.smartypants(s, smartypants.Attr.q | smartypants.Attr.u)


class ModelMixin:
    def get_absolute_url(self):
        purl = self.permaurl()
        if not purl.startswith('/'):
            purl = '/' + purl
        return purl

    @staticmethod
    def parse_xml(xmlfile):
        try:
            return etree.parse(xmlfile).getroot()
        except Exception as e:
            raise Exception("Couldn't parse %r: %s" % (xmlfile, e))

    def add_feature(self, feature):
        if feature not in self.features:
            if self.features:
                self.features += ";"
            self.features += feature

    def add_features_from_text(self, dom):
        if bool(dom.findall('.//svg:svg', namespaces={'svg': 'http://www.w3.org/2000/svg'})):
            self.add_feature("svg")
        if bool(dom.findall('.//blockquote[@class="twitter-tweet"]')):
            self.add_feature("tweets")


class Article(models.Model, ModelMixin):
    """ An article represented by a .px file.
    """
    path = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=200)
    text = models.TextField()
    comments = models.BooleanField(default=False)
    sort = models.IntegerField(default=500)
    sitemap = models.BooleanField(default=True)
    lang = models.CharField(max_length=5)
    copyright = models.TextField()
    meta = models.TextField()
    scripts = models.TextField()    # Space-separated script URLs.
    style = models.TextField()      # Extra css for the page.
    features = models.TextField()   # A set of slugs of features in use on the page.

    def __repr__(self):
        return "<Article %r>" % self.title

    def to_html(self):
        dpath = self.path
        dpath = dpath[:dpath.rfind('.')] + ".html"
        return content_transform(self.path, fix_blog_links(self.text), params={'dpath':string_param(dpath)})

    def permaurl(self, short=False):
        purl = self.path.replace('.px', '.html')
        if short:
            if purl.endswith('/index.html'):
                # Strip off /index.html suffix, if any.
                purl = purl[:-len('/index.html')]
            elif purl == 'index.html':
                purl = ''
        return '/' + purl

    @staticmethod
    def create_from_px(pxfile, root):
        p = ModelMixin.parse_xml(pxfile)
        art = Article()
        art.title = nice_text(p.get('title'))
        art.path = pxfile[len(root)+1:].replace('\\', '/')
        art.text = etree.tostring(p).decode('utf8')
        art.sitemap = (p.get('sitemap', 'yes') != 'no')
        art.lang = p.get('lang', 'en')
        art.sort = int(p.get('order', '500'))
        art.comments = bool(p.findall('pagecomments'))

        for copyright in p.findall('copyright'):
            art.copyright = copyright.text

        art.meta = ""
        if p.get('index', 'yes') == "no":
            art.meta += "<meta name='ROBOTS' content='NOINDEX'>"

        # These should really be sub-elements, because how come blog posts
        # have <title> and <body>, but page doesn't?
        art.scripts = p.get('scripts', '')
        art.style = p.get('style', '')

        art.add_features_from_text(p)

        art.save()

        # Save the history.
        for what in p.findall('history/what'):
            ww = WhatWhen(when=datetime_from_8601(what.get('when')), what=what.text, article=art)
            ww.save()

        # Save the section.
        for section in p.findall('section'):
            s = Section()
            if section.get('title'):
                s.title = section.get('title')
            s.sitemap = (section.get('sitemap', 'yes') != 'no')
            s.sort = int(section.get('order', '500'))
            s.article = art
            s.save()

        save_plain_text(p)


class Section(models.Model):
    """ An identified section in the site.
    """
    title = models.CharField(max_length=200)
    sort = models.IntegerField(default=500)
    sitemap = models.BooleanField(default=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __repr__(self):
        return "<Section %r sort=%r sitemap=%r article=%r>" % (
            self.title, self.sort, self.sitemap, self.article
        )


class WhatWhen(models.Model):
    """ An edit indicator, many to one with pages.
    """
    when = models.DateTimeField()
    what = models.CharField(max_length=200)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    def __repr__(self):
        return "<WhatWhen %s: %r>" % (self.when, self.what)


class Tag(models.Model, ModelMixin):
    """ A tag for blog entries.
    """
    tag = models.CharField(max_length=50)
    name = models.CharField(max_length=50, null=True)
    about = models.TextField(null=True)
    sidebar = models.BooleanField()
    #related = models.ManyToManyField('self') # TODO
    # TODO: there's a <tag> thingy too, but that seems really redundant...

    class Meta:
        ordering = ['name']

    def __repr__(self):
        return "<Tag: %s>" % self.tag

    @staticmethod
    def create_from_xml(xmlfile):
        root = ModelMixin.parse_xml(xmlfile)
        for cat in root.findall('category'):
            tag = Tag()
            tag.tag = cat.get('id')
            tag.name = cat.find('name').text
            tag.about = cat.find('about').text
            tag.sidebar = cat.get('sidebar', '') == 'y'
            tag.save()

    def permaurl(self):
        return "/blog/tag/%s.html" % self.tag

    def entry_set_no_drafts(self):
        return self.entry_set.filter(draft=False)

    @property
    def hashtag(self):
        """The name, but for a hashtag."""
        return self.name.replace(' ', '-').lower()


class Link(models.Model, ModelMixin):
    """ A link to somewhere else, for blogroll and via.
    """
    href = models.CharField(max_length=1000)
    slug = models.CharField(max_length=30)
    text = models.CharField(max_length=200)
    sidebar = models.BooleanField(default=False)

    def __repr__(self):
        return "<Link %s>" % self.slug

    @staticmethod
    def create_from_lx(lxfile):
        root = ModelMixin.parse_xml(lxfile)
        for l in root.findall('.//link'):
            link = Link()
            link.slug = l.get('id')
            link.href = l.get('href')
            link.text = l.find('title').text
            link.save()

        for cat in root.findall('.//category'):
            if cat.get('name') == 'Blogs':
                for l in cat.findall('link'):
                    link = Link.objects.get(slug=l.get('id'))
                    link.sidebar = True
                    link.save()


# Entries have drafts, and it's almost always right to exclude them, so we
# have custom managers.
class DraftsManager(models.Manager):
    def get_queryset(self):
        return super(DraftsManager, self).get_queryset().filter(draft=True)

class NoDraftsManager(models.Manager):
    def get_queryset(self):
        return super(NoDraftsManager, self).get_queryset().filter(draft=False)


class Entry(models.Model, ModelMixin):
    """ A blog entry, slurped from a .bx file.
    """
    path = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=200)
    when = models.DateTimeField(db_index=True)
    draft = models.BooleanField()
    text = models.TextField()
    tags = models.ManyToManyField(Tag)
    slug = models.CharField(max_length=200, db_index=True)
    comments_closed = models.BooleanField()
    features = models.TextField()   # A set of slugs of features in use on the page.

    # Use all_entries to get absolutely everything.
    all_entries = models.Manager()
    objects = NoDraftsManager()
    drafts = DraftsManager()

    def __repr__(self):
        return "<Entry %s: %r>" % (self.when, self.title)

    @staticmethod
    def create_from_bx(bxfile):
        root = ModelMixin.parse_xml(bxfile)
        for e in root.findall('entry'):
            ent = Entry()
            assert bxfile.startswith("./")
            ent.path = bxfile[2:].replace('\\', '/')
            ent.title = nice_text(e.find('title').text)
            ent.text = etree.tostring(e).decode('utf8')
            ent.comments_closed = (e.get('comments_closed', 'n') == 'y')
            ent.when = datetime_from_8601(e.get('when'))
            ent.draft = (e.get('draft', 'n') == 'y') or ent.when > datetime.datetime.now()
            ent.slug = e.get('slug', slug_from_text(ent.title))
            ent.add_features_from_text(e)

            if ent.draft:
                ent.title += " (draft)"

            ent.save()

            for cat in e.findall('category'):
                if cat.text:
                    try:
                        tag = Tag.objects.get(tag=cat.text)
                    except Tag.DoesNotExist:
                        tags = Tag.objects.all().order_by('tag')
                        all_tags = " ".join([t.tag for t in tags])
                        raise Exception("No such tag as %r, choices are: %s" % (cat.text, all_tags))
                    ent.tags.add(tag)

            for via in e.findall('via'):
                if via.get('id'):
                    link = Link.objects.get(slug=via.get('id'))
                    v = Via(entry=ent, link=link)
                    v.save()
                elif via.text:
                    v = Via(entry=ent, href=via.get('href'), text=via.text)
                    v.save()

            save_plain_text(e.find("body"))

    def to_brief_html(self):
        return self.to_html(blogmode='brief')

    def to_html(self, blogmode='full'):
        params={
            'dpath':    string_param(""),
            'blogmode': string_param(blogmode),
            'title':    string_param(self.title),
            'permaurl': string_param(self.permaurl()),
            }
        return content_transform(self.title, fix_blog_links(self.text), 'body', params=params)

    def permaurl(self):
        return "/blog/%04d%02d/%s.html" % (self.when.year, self.when.month, self.slug)

    def monthurl(self):
        return "/blog/archive/year%04d.html#month%04d%02d" % (self.when.year, self.when.year, self.when.month)

    def dateurl(self):
        return "/blog/archive/date%02d%02d.html" % (self.when.month, self.when.day)

    def entryid(self):
        return self.when.strftime("e%Y%m%dT%H%M%S")


class Via(models.Model):
    """ A source for a blog entry, either a link_id or an href and text.
    """
    link = models.ForeignKey(Link, null=True, on_delete=models.CASCADE)
    href = models.CharField(max_length=1000, null=True)
    text = models.CharField(max_length=200, null=True)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)


# Forms to deal with properly:
#   <a href='blog/200409.html#e20040928T070525'>
#   <a href='http://www.nedbatchelder.com/blog/200204.html#e20020401T145521'>
#   <a href='blog/20060105T073557.html'>
#   <a href='http://www.nedbatchelder.com/blog/20020721T095152.html'>

re_blog_url = re.compile(
    r'''(?<= href=['"])'''                                  # Match must be preceded by href='
    r'''(http://www.nedbatchelder.com/)?blog/'''            # They might be full URLs
    "("
        r'''\d{6}.html#e\d{8}T\d{6}'''      # 200409.html#e20040928T070525
    "|"
        r'''\d{8}T\d{6}\.html'''            # 20020721T095152.html
    ")"
    )

def fix_blog_link(match):
    url = match.group()
    if url.endswith(".html"):
        whenid = url[-20:-5]
    else:
        whenid = url[-15:]
    when = time.strptime(whenid, "%Y%m%dT%H%M%S")
    try:
        entry = Entry.objects.get(when=datetime.datetime(*when[:6]))
    except Entry.DoesNotExist:
        return "/blog/no_such_article.html"
    return entry.permaurl()

def fix_blog_links(text):
    """ Replace links to blog posts with the correct URLs.
    """
    return re_blog_url.sub(fix_blog_link, text)
