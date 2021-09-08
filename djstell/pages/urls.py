from django.urls import path, re_path, register_converter
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


urlpatterns = [
    re_path(r'^(?:index.html)?$', dpv.index),
    re_path(r'^blog(?:/index.html)?$', dpv.blogmain),
    path('blog/<yyyy:year><mm:month>/<slug:slug>.html', dpv.entry),

    path('blog/tags.html', dpv.tags),
    path('blog/tag/none.html', dpv.untagged),
    path('blog/tag/<slug:slug>.html', dpv.tag),

    path('blog/archive/year<yyyy:year>.html', dpv.archiveyear),
    path('blog/archive/date<mm:month><dd:day>.html', dpv.archivedate),
    path('blog/archive/all.html', dpv.archiveall),
    path('blog/drafts.html', dpv.drafts),

    path('blog/rss.xml', dpv.blog_rss),
    path('blog/planetpython.xml', dpv.tags_rss, {'tags': PLANET_PYTHON_TAGS}),
    path('blog/moved.php', dpv.blog_moved_php),

    re_path(r'^(?P<path>(text|code|site)/?.*)$', dpv.article),
    re_path(r'^(?P<path>err404.html)$', dpv.article),

    path('crash', dpv.crash),

    path('0inc/sidebar_<slug:which>.inc', dpv.sidebar),
    path('0inc/navbar.inc', dpv.navbar),
    path('0inc/metatags.inc', dpv.metatags),
    ]
