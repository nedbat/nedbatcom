from django.conf.urls import url
from django.views.generic.base import TemplateView

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

urlpatterns = [
    url(r'^index.html$', dpv.index),
    url(r'^blog/index.html$', dpv.blogmain),
    url(r'^blog/(?P<year>\d\d\d\d)(?P<month>\d\d)/(?P<slug>[^/]+).html$', dpv.entry),

    url(r'^blog/tags.html$', dpv.tags),
    url(r'^blog/tag/none.html$', dpv.untagged),
    url(r'^blog/tag/(?P<slug>.*).html$', dpv.tag),

    url(r'^blog/archive/year(?P<year>\d\d\d\d).html$', dpv.archiveyear),
    url(r'^blog/archive/date(?P<month>\d\d)(?P<day>\d\d).html$', dpv.archivedate),
    url(r'^blog/archive/all.html$', dpv.archiveall),
    url(r'^blog/drafts.html$', dpv.drafts),

    url(r'^blog/rss.xml$', dpv.blog_rss),
    url(r'^blog/planetpython.xml$', dpv.tags_rss, {'tags': PLANET_PYTHON_TAGS}),
    url(r'^blog/moved.php$', dpv.blog_moved_php),

    url(r'^(?P<path>(text|code|site)/.*)$', dpv.article),
    url(r'^(?P<path>err404.html)$', dpv.article),

    url(r'^sidebar_(?P<which>\w+).inc$', dpv.sidebar),
    url(r'^navbar.inc$', dpv.navbar),
    url(r'^footer.inc$', dpv.footer),
    url(r'^metatags.inc$', dpv.metatags),
    ]
