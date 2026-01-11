from django.urls import path, re_path, register_converter
from django.views.generic.base import RedirectView

import djstell.pages.views as dpv

PLANET_PYTHON_TAGS = [
    'python', 'pycon', 'math', 'proglang', 'ruby', 'js',
    'coverage', 'cog', 'mycode',
    'browsers', 'charset', 'coding', 'compsci', 'concurrency',
    'db', 'debugging', 'devmindset', 'development', 'django', 'ide',
    'exceptions', 'feeds', 'geeky', 'regex', 'security', 'srcctrl',
    'testing', 'webpage',
    'windows', 'mac', 'unix',
    'jupyter', 'opensource', 'presentations', 'linters', 'regex',
]

def digits(n):
    class DigitConverter:
        regex = f'[0-9]{{{n}}}'

        def to_python(self, value):
            return int(value)

        def to_url(self, value):
            return f'%0{n}d' % value
    return DigitConverter

register_converter(digits(4), 'yyyy')
register_converter(digits(2), 'mm')
register_converter(digits(2), 'dd')

redirect = RedirectView.as_view

urlpatterns = [
    # Old coverage links shouldn't get .html stripped, so handle them before
    # the html-stripping rule.
    re_path(r'^code/coverage/?$', redirect(url='https://coverage.readthedocs.io')),
    path('code/coverage/beta/<path:path>', redirect(url='https://coverage.readthedocs.io/en/latest/%(path)s')),
    path('code/coverage/<path:path>', redirect(url='https://coverage.readthedocs.io/en/latest/%(path)s')),
    path('code/modules/coverage.html', redirect(url='https://coverage.readthedocs.io')),
    path('code/modules/coverage-<path:path>', redirect(url='https://pypi.org/project/coverage/#files')),

    # Old .html URLs redirect to no-extension versions.
    re_path(r'^(?P<path>.+)\.html$', redirect(url='/%(path)s', permanent=True)),
    # URLs ending in slashes redirect to no-slash versions.
    re_path(r'^(?P<path>.+)/$', redirect(url='/%(path)s', permanent=True)),
    # Old blog archive URLs redirect to new ones.
    re_path(r'blog/archive/year(?P<year>\d{4})', redirect(url='/blog/%(year)s', permanent=True)),
    re_path(r'blog/archive/date(?P<date>\d{4})', redirect(url='/blog/date/%(date)s', permanent=True)),
    re_path(r'blog/archive/all', redirect(url='/blog/all', permanent=True)),

    re_path(r'^$', dpv.index),
    re_path(r'^blog$', dpv.blogmain),

    path('blog/<yyyy:year><mm:month>/<slug:slug>', dpv.entry),

    path('blog/tags', dpv.tags),
    path('blog/tag/none', dpv.untagged),
    path('blog/tag/<slug:slug>', dpv.tag),

    path('blog/<yyyy:year>', dpv.archiveyear),
    path('blog/date/<mm:month><dd:day>', dpv.archivedate),
    path('blog/all', dpv.archiveall),
    path('blog/drafts', dpv.drafts),
    path('blog/classics', dpv.classics_home),
    path('blog/classics/<slug:slug>', dpv.classics),

    re_path(r'^blog/(?:rss|rssfull|atom).xml$', dpv.blog_rss),
    path('blog/planetpython.xml', dpv.tags_rss, {'tags': PLANET_PYTHON_TAGS}),
    path('summary.json', dpv.summary),
    re_path(r'^blog/(?P<whenid>\d{8}T\d{6})$', dpv.entry_by_date),

    re_path(r'^code/cog/?$', redirect(url='https://cog.readthedocs.io')),

    path('NedBatchelder.pdf', redirect(url='Ned-Batchelder-Resume.pdf')),

    re_path(r'^(?P<path>(text|code|site))$', dpv.article),
    re_path(r'^(?P<path>(text|code|site)/.*)$', dpv.article),
    re_path(r'^(?P<path>err404)$', dpv.article),

    path('crash', dpv.crash),

    re_path(r'^blueripple/?$', redirect(url='https://web.archive.org/web/20010401130155/http://blueripple.com/')),
]
