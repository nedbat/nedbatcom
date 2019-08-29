#!/usr/bin/env python3
# Load the database for nedbatchelder.com

import sys
import operator
import traceback

from path import Path
from django.db import transaction
from djstell.pages.models import Article, Section, Entry, Tag, Link


root = Path(".")
page_sources = 'pages'.split()
blog_sources = 'blog 0blog 1blog'.split()
blog_pattern = '*.bx'
page_pattern = '*.px'

def walk_pattern(root, glob):
    """Find all files matching glob anywhere in root"""
    for f in root.glob(glob):
        yield f
    for d in root.walkdirs():
        for f in d.glob(glob):
            yield f

@transaction.atomic
def clean_data():
    for klass in [Article, Section, Entry, Tag, Link]:
        klass.objects.all().delete()
    # Entry.objects.all doesn't include drafts, so nuke them specially:
    Entry.drafts.all().delete()

@transaction.atomic
def load_categories():
    Tag.create_from_xml(str(root/'categories.xml'))

@transaction.atomic
def load_entries():
    for subdir in blog_sources:
        files = list(walk_pattern(root/subdir, blog_pattern))
        print("Loading %d files from %s" % (len(files), subdir))
        for f in files:
            try:
                Entry.create_from_bx(str(f))
            except Exception as e:
                raise Exception("Couldn't create from bx '%s': %s" % (f, e))

@transaction.atomic
def load_articles():
    for subdir in page_sources:
        files = list(walk_pattern(root/subdir, page_pattern))
        print("Loading %d pages from %s" % (len(files), subdir))
        for f in files:
            Article.create_from_px(str(f), str(root/subdir))

@transaction.atomic
def create_bogus_blog_pages():
    blog = Article(path='blog/index.px', title='Blog', text='')
    blog.save()
    Section(article=blog, title='Blog').save()

@transaction.atomic
def load_links():
    Link.create_from_lx(str(root/'links/blogs.lx'))

def load_all():
    clean_data()
    load_categories()
    load_links()
    load_entries()
    load_articles()
    create_bogus_blog_pages()

    # Stats
    print()
    print("%d total blog posts" % (Entry.objects.all().count()))

    # Show all the slugs
    if 0:
        for ent in Entry.objects.all().order_by('title'):
            print("%4d %s: %s" % (ent.id, ent.when, ent.slug))

    # Yearly census
    if 0:
        years = Entry.objects.dates('when', 'year')
        for year in years:
            y = year.year
            print("%s: %d entries" % (y, Entry.objects.filter(when__year=y).count()))

    # Show draft titles
    if 1:
        drafts = Entry.drafts.all()
        print("%d drafts:" % (len(drafts)))
        for d in sorted(drafts, key=operator.attrgetter('when')):
            print(d.when, d.title)

    if 0:
        print("\nTags:")
        for t in Tag.objects.all().order_by('tag'):
            print("%s: %d entries" % (t.tag, t.entry_set.count()))

if __name__ == '__main__':
    load_all()
