# Generate HTML pages for nedbatchelder.com

import logging, os, shutil, socket, sys, time

from django.conf import settings
from django.core.management import call_command

from stellated import XuffApp

import generator
import loadpages
import password

from djstell.pages.models import Entry, Article, Tag


def timed(fn):
    def wrapped(*args, **kwargs):
        start = time.time()
        ret = fn(*args, **kwargs)
        now = time.time()
        print "%s time: %.2fs" % (fn.__name__, now - start)
        return ret
    return wrapped


class CmdLine(object):
    def __init__(self):
        self.xuff = XuffApp.XuffApp()
        self.BASE = None
        self.ROOT = r'html'
        self.HTACCESS = None
        self.PHPINI = None
        self.PHP_INCLUDE = True
        self.all_words = "clean load make upload"
        self.text_ext='''
            *.html *.css *.xslt *.js *.txt *.xml *.inc
            *.ps *.py *.pyw *.cmd *.h *.c *.cpp *.ida *.scm *.php *.htaccess *.ini
            *.svg
            '''
        self.binary_ext='''
            *.gif *.jpg *.png *.mp3 *.exe *.ico *.swf *.doc *.nef *.pdf *.ai *.dmg
            *.zip *.gz *.tgz
            *.ttf
            '''
        self.use_processes = True

    def do_local(self):
        self.BASE = 'http://%s' % (socket.gethostbyname(socket.gethostname()))
        self.ROOT = '../www'
        self.HTACCESS = 'local.htaccess'
        self.all_words = "load make"    # Don't clean: it clobbers reactor.

    def do_file(self):
        self.BASE = 'file:///Users/ned/web/stellated/html_local'
        self.ROOT = 'html_local'
        self.PHP_INCLUDE = False

    def do_tch(self):
        self.BASE = 'http://nedbatchelder.com'
        self.HTACCESS = 'totalchoice.htaccess'
        self.FTP = dict(
            host='72.9.232.138', hostdir='www',
            user='nedbatc', password=password.TCH,
            src='html',
            text=self.text_ext,
            binary=self.binary_ext,
            md5file='totalchoice.md5',
            )

    def do_wf(self):
        self.BASE = 'http://nedbatchelder.com'
        self.HTACCESS = 'webfaction.htaccess'
        self.PHPINI = 'webfaction.php.ini'
        self.FTP = dict(
            host='nedbat.webfactional.com', hostdir='webapps/main',
            user='nedbat', password=password.WEBFACTION,
            src='html',
            text=self.text_ext,
            binary=self.binary_ext,
            md5file='webfaction.md5',
            )

    def do_nednet(self):
        self.BASE = 'http://nedbatchelder.net'
        self.HTACCESS = 'nednet.htaccess'
        self.FTP = dict(
            host='nedbatchelder.net', hostdir='nedbatchelder.net',
            user='nedbat', password=password.NEDNET,
            src='html',
            text=self.text_ext,
            binary=self.binary_ext,
            md5file='nedbat.md5',
            )

    def generate(self, baseurl, dst):
        settings.SERVER_NAME = "example.com"    # Doesn't matter...
        settings.WEB_ROOT = dst
        settings.BASE = baseurl
        settings.PHP = False
        settings.PHP_INCLUDE = self.PHP_INCLUDE

        resources = [
            Entry.objects,
            Article,
            Tag,
            '/blog/index.html',
            '/blog/tags.html',
            '/blog/tag/none.html',
            '/blog/rss.xml',
            '/blog/planetpython.xml',
            '/blog/archiveall.html',
            '/blog/moved.php',
            '/sidebar_blog.inc',
            '/sidebar_page.inc',
            '/index.html',
            ]

        months = set(e.monthurl() for e in Entry.objects.all())
        resources += list(months)

        years = [ '/blog/archive%4d.html' % d.year for d in Entry.objects.dates('when', 'year') ]
        resources += years

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
                *.html *.css *.xslt *.js *.gif *.jpg *.png *.svg *.ttf
                *.txt *.ida *.php *.ico *.htaccess *.xml
                *.ps *.py *.pyw *.exe *.cmd *.zip *.cpp *.h *.scm *.pdf *.gz *.tgz *.dmg
                '''
            )
        self.xuff.copytree(src='pix', dst=dst+"/pix",
            include='*.gif *.jpg *.png *.svg *.swf'
            )
        self.xuff.copytree(src='blog', dst=dst+"/blog",
            include='*.gif *.jpg *.png *.svg *.swf'
            )
        self.xuff.copytree(src='files', dst=dst+"/files", include='*.*')

    @timed
    def do_clean(self):
        if os.path.exists(settings.DATABASES['default']['NAME']):
            os.remove(settings.DATABASES['default']['NAME'])
        if os.access(self.ROOT, os.F_OK):
            shutil.rmtree(self.ROOT)

    @timed
    def do_load(self):
        call_command('syncdb', verbosity=False, interactive=False)
        loadpages.load_all()

    def do_1blog(self):
        loadpages.blog_sources = ['1blog']

    def do_narrow(self):
        """Total hack expedient to only process some blog posts."""
        # Change this pattern if you want to fiddle with another one.
        loadpages.blog_pattern = "*thing*.bx"

    def do_slow(self):
        self.use_processes = False

    @timed
    def do_make(self):
        self.generate(self.BASE, self.ROOT)
        self.copy_verbatim(self.ROOT)
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
                'http://nedbatchelder.com/blog'
                ]
            )

    def do_all(self):
        self.exec_words(self.all_words.split())

    def exec_words(self, argv):
        for word in argv:
            doit = getattr(self, 'do_'+word, None)
            if not doit:
                print "Don't understand: %s" % word
                return
            print ":: %s ::" % word
            doit()

    @timed
    def main(self, argv):
        start = time.clock()
        self.exec_words(argv)
        now = time.clock()

if __name__ == '__main__':
    cmdline = CmdLine()
    cmdline.main(sys.argv[1:])
