""" Stuff for understanding global structure.
"""

from djstell.pages.models import Article, Section
import os.path, pprint

class Page:
    def __init__(self):
        self.path
        self.title
        self.sort
        self.sitemap

class SiteMap:
    def __init__(self):
        self.map = {}   # from path to a page-like object

        # Load the articles
        for article in Article.objects.all():
            if article.section_set.all():
                section = article.section_set.all()[0]
                article.title = section.title
            self.map[article.path] = article

        self.top = []
        for section in Section.objects.all().order_by('sort', 'title'):
            p, f = os.path.split(section.article.path)
            if f == 'index.px' and p and '/' not in p:
                self.top.append((section.title, section.article.permaurl(short=True)))

    def top_levels(self):
        pass

    def top_areas(self):
        return self.top

sitemap = SiteMap()

if __name__ == '__main__':
    pprint.pprint(sitemap.top_areas())
