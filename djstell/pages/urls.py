from django.conf.urls.defaults import *

PLANET_PYTHON_TAGS = [
    'python', 'pycon', 'math', 'proglang', 'ruby', 'js',
    'coverage', 'cog', 'mycode',
    'browsers', 'charset', 'coding', 'compsci', 'concurrency',
    'db', 'debugging', 'devmindset', 'development', 'django', 'ide',
    'exceptions', 'feeds', 'geeky', 'regex', 'security', 'srcctrl',
    'testing', 'webpage',
    'windows', 'mac', 'unix',
    ]

urlpatterns = patterns('djstell.pages.views',
    (r'^index.html$', 'index'),
    (r'^blog/index.html$', 'blogmain'),
    (r'^blog/(?P<year>\d\d\d\d)(?P<month>\d\d).html$', 'month'),
    (r'^blog/(?P<year>\d\d\d\d)(?P<month>\d\d)/(?P<slug>[^/]+).html$', 'entry'),

    (r'^blog/tags.html$', 'tags'),
    (r'^blog/tag/none.html$', 'untagged'),
    (r'^blog/tag/(?P<slug>.*).html$', 'tag'),

    (r'^blog/archive(?P<year>\d\d\d\d).html$', 'archiveyear'),
    (r'^blog/archiveall.html$', 'archiveall'),

    (r'^blog/rss.xml$', 'blog_rss'),
    (r'^blog/planetpython.xml$', 'tags_rss', {'tags': PLANET_PYTHON_TAGS}),
    (r'^blog/moved.php$', 'blog_moved_php'),

    (r'^(?P<path>(text|code|site)/.*)$', 'article'),
    (r'^(?P<path>err404.html)$', 'article'),

    (r'^sidebar_(?P<which>\w+).inc$', 'sidebar'),
    )

urlpatterns += patterns('',
    (r'^tabblo_badge_(?P<tabblos>\w+).html$', 'django.views.generic.simple.direct_to_template', {'template': 'tabblo_badge.html'}),
    )
