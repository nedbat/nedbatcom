# Generate HTML pages for nedbatchelder.com

import datetime
import glob
import logging
import os
import os.path
import shutil
import socket
import sys
import time

import django
django.setup()

from django.conf import settings
from django.core.management import call_command

from stellated import XuffApp

import generator
import loadpages
import password
import sass

from djstell.pages.models import Entry, Article, Tag


def timed(fn):
    def wrapped(*args, **kwargs):
        start = time.time()
        ret = fn(*args, **kwargs)
        now = time.time()
        print("%s time: %.2fs" % (fn.__name__, now - start))
        return ret
    return wrapped


class CmdLine(object):
    def __init__(self):
        self.xuff = XuffApp.XuffApp()
        self.BASE = None
        self.EXT_BASE = None
        self.ROOT = r'html'
        self.HTACCESS = None
        self.PHPINI = None
        self.PHP_INCLUDE = True
        self.all_words = "clean load make upload"
        self.text_ext='''
            *.html *.css *.xslt *.js *.txt *.xml *.inc
            *.ps *.py *.pyw *.cmd *.h *.c *.cpp *.ida *.scm *.php *.htaccess *.ini
            *.svg *.ipynb
            '''
        self.binary_ext='''
            *.gif *.jpg *.png *.mp3 *.exe *.ico *.swf *.doc *.nef *.pdf *.ai *.dmg
            *.zip *.gz *.tgz
            *.ttf *.woff2
            '''
        self.use_processes = True
        self.messages = []

    def do_local(self):
        self.BASE = '//%s' % (socket.gethostbyname(socket.gethostname()))
        self.ROOT = '../www'
        self.HTACCESS = 'local.htaccess'
        self.WWWROOT = os.path.abspath(self.ROOT)
        self.all_words = "load make"    # Don't clean: it clobbers reactor.

    def do_pylocal(self):
        host = socket.gethostbyname(socket.gethostname())
        port = 8123
        self.BASE = f"//{host}:{port}"
        self.ROOT = "../www"
        self.WWWROOT = os.path.abspath(self.ROOT)
        self.PHP_INCLUDE = False
        self.messages.append(
            f"Simple local server:\n  sudo -v; sudo python -m http.server -b {host} -d ../www {port} & open http://{host}:{port}"
        )

    def do_file(self):
        self.BASE = 'file:///Users/ned/web/stellated/html_local'
        self.ROOT = 'html_local'
        self.WWWROOT = os.path.abspath(self.ROOT)
        self.PHP_INCLUDE = False

    def do_wf(self):
        self.BASE = '//nedbatchelder.com'
        self.EXT_BASE = 'https://nedbatchelder.com'
        self.HTACCESS = 'webfaction.htaccess'
        self.PHPINI = 'webfaction.php.ini'
        self.WWWROOT = '/home/nedbat/webapps/main'
        self.FTP = dict(
            host='nedbat.webfactional.com', hostdir='webapps/main',
            user='nedbat', password=password.WEBFACTION,
            src='html',
            text=self.text_ext,
            binary=self.binary_ext,
            md5file='webfaction.md5',
            )

    def do_nednet(self):
        self.BASE = '//nedbatchelder.net'
        self.HTACCESS = 'nednet.htaccess'
        self.WWWROOT = '/home/nedbat/nedbatchelder.net'
        self.PHP_INCLUDE = False
        self.FTP = dict(
            host='nedbatchelder.net', hostdir='nedbatchelder.net',
            user='nedbat', password=password.NEDNET,
            src='html',
            text=self.text_ext,
            binary=self.binary_ext,
            md5file='nedbat.md5',
            )

    def generate(self, dst):
        settings.SERVER_NAME = "example.com"    # Doesn't matter...
        settings.WEB_ROOT = dst
        settings.BASE = self.BASE
        settings.WWWROOT = self.WWWROOT
        if self.EXT_BASE:
            settings.EXT_BASE = self.EXT_BASE
        elif ':' in self.BASE:
            settings.EXT_BASE = self.BASE
        else:
            settings.EXT_BASE = 'http:' + self.BASE
        settings.PHP = False
        settings.PHP_INCLUDE = self.PHP_INCLUDE

        resources = [
            Entry.all_entries,
            Article,
            Tag,
            '/blog/index.html',
            '/blog/tags.html',
            '/blog/tag/none.html',
            '/blog/rss.xml',
            '/blog/planetpython.xml',
            '/blog/archive/all.html',
            '/blog/moved.php',
            '/blog/drafts.html',
            '/0inc/sidebar_blog.inc',
            '/0inc/sidebar_page.inc',
            '/0inc/navbar.inc',
            '/0inc/metatags.inc',
            '/index.html',
            ]

        resources += ['/blog/archive/year%4d.html' % d.year for d in Entry.objects.dates('when', 'year')]

        dates = []
        date = datetime.datetime(2004, 1, 1)        # Use a leap year
        while date.year == 2004:
            dates.append((date.month, date.day))
            date += datetime.timedelta(days=1)

        resources += ['/blog/archive/date%02d%02d.html' % date for date in dates]

        generator.quick_publish(resources, use_processes=self.use_processes)

        # Build the JS file as the concatenation of others.
        with open("js/ingredients.txt") as ingredients:
            js = ingredients.read().split()
        with open(dst+"/nedbatchelder.js", "w") as outjs:
            for f in js:
                with open("js/"+f) as jsin:
                    outjs.write(jsin.read())
                outjs.write("\n")

    def copy_verbatim(self, dst):
        self.xuff.copytree(src='pages', dst=dst,
            include='''
                *.html *.css *.xslt *.js *.gif *.jpg *.png *.svg *.ttf *.woff2
                *.txt *.ida *.php *.ico *.htaccess *.xml
                *.ps *.py *.pyw *.exe *.cmd *.zip *.cpp *.h *.scm *.pdf *.gz *.tgz *.dmg
                *.ipynb
                '''
            )
        self.xuff.copytree(src='pix', dst=dst+"/pix",
            include='*.gif *.jpg *.png *.svg *.swf'
            )
        self.xuff.copytree(src='blog', dst=dst+"/blog",
            include='*.gif *.jpg *.png *.svg *.swf'
            )
        self.xuff.copytree(src='files', dst=dst+"/files", include='*.*')

    def run_sass(self, sassname, dst):
        """Compile a Sass file named `sassname` into the `dst` directory"""
        basename = os.path.splitext(os.path.basename(sassname))[0]
        output_file = os.path.join(dst, basename + '.css')
        css = sass.compile(filename=sassname, output_style="compressed")
        with open(output_file, "w") as css_out:
            css_out.write(css)

    @timed
    def do_clean(self):
        if os.path.exists(settings.DATABASES['default']['NAME']):
            os.remove(settings.DATABASES['default']['NAME'])
        if os.access(self.ROOT, os.F_OK):
            shutil.rmtree(self.ROOT)

    @timed
    def do_load(self):
        call_command('migrate', verbosity=False, interactive=False)
        loadpages.load_all()

    def do_1blog(self):
        loadpages.blog_sources = ['1blog']

    def do_narrow(self):
        """Total hack expedient to only process some blog posts."""
        # Change this pattern if you want to fiddle with another one.
        loadpages.blog_pattern = "*why*.bx"

    def do_pnarrow(self):
        """Total hack expedient to only process some pages."""
        # Change this pattern if you want to fiddle with another one.
        loadpages.page_pattern = "*x*.px"

    def do_slow(self):
        self.use_processes = False

    @timed
    def do_make(self):
        self.generate(self.ROOT)
        self.copy_verbatim(self.ROOT)
        self.do_support()

    @timed
    def do_support(self):
        for sassfile in glob.glob("style/[a-z]*.scss"):
            self.run_sass(sassfile, self.ROOT)
        if self.HTACCESS:
            self.xuff.copyfile(self.HTACCESS, self.ROOT+"/.htaccess")
        if self.PHPINI:
            self.xuff.copyfile(self.PHPINI, self.ROOT+"/php.ini")

    @timed
    def do_upload(self):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s", "%H:%M:%S"))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
        self.xuff.upload(**self.FTP)

    def do_ping(self):
        self.xuff.xmlrpc(
            url='http://rpc.pingomatic.com/RPC2',
            object='weblogUpdates',
            method='ping',
            args=[
                'Ned Batchelder',
                'https://nedbatchelder.com/blog'
                ]
            )

    def do_all(self):
        self.exec_words(self.all_words.split())

    def exec_words(self, argv):
        for word in argv:
            doit = getattr(self, 'do_'+word, None)
            if not doit:
                print("Don't understand: %s" % word)
                return
            print(":: %s ::" % word)
            doit()
        for message in self.messages:
            print(message)

    @timed
    def main(self, argv):
        self.exec_words(argv)

if __name__ == '__main__':
    cmdline = CmdLine()
    cmdline.main(sys.argv[1:])
