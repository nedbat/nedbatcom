""" Stuff for understanding global structure.
"""

from djstell.pages.models import Article, Section
import os.path, pprint

class SiteMap:
    def __init__(self):
        self.top = []
        for section in Section.objects.all().order_by('sort', 'title'):
            p, f = os.path.split(section.article.path)
            if f == 'index.px' and p and '/' not in p:
                self.top.append((section.title, section.article.permaurl(short=True)))

    def top_areas(self):
        return self.top

if __name__ == '__main__':
    sitemap = SiteMap()
    pprint.pprint(sitemap.top_areas())
