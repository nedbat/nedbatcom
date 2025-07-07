# Generate HTML pages for nedbatchelder.com

import datetime
import glob
import logging
import os
import os.path
import shutil
import subprocess
import sys
import time

import django
django.setup()

from django.conf import settings
from django.core.management import call_command

from blogtools import XuffApp

import loadpages
import sass


def timed(fn):
    def wrapped(*args, **kwargs):
        start = time.time()
        ret = fn(*args, **kwargs)
        now = time.time()
        print("%s time: %.2fs" % (fn.__name__, now - start))
        return ret
    return wrapped


def run_cmd(*cmd):
    process = subprocess.Popen([*cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in process.stdout:
        sys.stdout.buffer.write(line)


class CmdLine(object):
    def __init__(self):
        self.xuff = XuffApp.XuffApp()
        self.BASE = None
        self.ROOT = "html"
        self.COPY_FILES = []
        self.COPY_TREES = []
        self.user_data = None
        self.all_words = "clean load make upload"
        self.text_ext='''
            *.html *.css *.xslt *.js *.txt *.xml
            *.ps *.py *.pyw *.cmd *.h *.c *.cpp *.ida *.scm
            *.htaccess *.ini *.env *.service
            *.svg *.ipynb
            webfinger atproto-did
            '''
        self.binary_ext='''
            *.gif *.jpg *.JPG *.png *.mp3 *.exe *.ico *.doc *.pdf *.ai
            *.zip *.gz *.tgz
            *.ttf *.woff2
            '''
        self.messages = []

    def do_live(self):
        self.BASE = "http://127.0.0.1:8000"
        self.ROOT = "live"
        self.VERB_ROOT = "live/public"
        self.user_data = "deploy/live_users.json"

    def do_nednet(self):
        self.dreamhost("nedbatchelder.net", "nednet")

    def do_nedcom(self):
        self.dreamhost("nedbatchelder.com", "nedcom")

    def dreamhost(self, domain, slug):
        self.slug = slug
        self.BASE = f'//{domain}'
        self.ROOT = "to_dh"
        self.VERB_ROOT = "to_dh/public"
        self.COPY_FILES = [
            (f"deploy/.env", ".env"),
            ("deploy/dreamhost_public.htaccess", "public/.htaccess"),   # This has no effect any more?
            ("deploy/wsgi.py", "wsgi.py"),
            (f"deploy/{slug}.service", f"{slug}.service"),
        ]
        self.COPY_TREES = [
            ("../blogtools", "blogtools"),
            ("requirements", "requirements"),
        ]
        self.user_data = f"deploy/{slug}_users.json"
        self.server = "dreamhost"
        self.RSYNC_DST = f"{self.server}:{domain}"
        self.all_words = "clean load copy_verbatim copy_live support collectstatic djstell timestamps upload rsyncdb restart"
        self.FTP = dict(
            host="nedbatchelder.net", hostdir=domain,
            user='nedbat', password=os.environ["DREAMHOST_PASSWORD"],
            src=self.ROOT,
            text=self.text_ext,
            binary=self.binary_ext,
            md5file=f'deploy/{slug}.md5',
            )

    @timed
    def do_copy_verbatim(self):
        dst = self.VERB_ROOT
        self.xuff.copytree(src='pages', dst=dst,
            include='''
                *.html *.css *.xslt *.js *.gif *.jpg *.png *.svg *.ttf *.woff2
                *.txt *.ida *.php *.ico *.xml
                *.ps *.py *.pyw *.exe *.cmd *.zip *.cpp *.h *.scm *.pdf *.gz *.tgz *.dmg
                *.ipynb
                '''
            )
        self.xuff.copytree(src='pix', dst=dst+"/pix",
            include='*.gif *.jpg *.JPG *.png *.svg *.swf'
            )
        self.xuff.copytree(src='files', dst=dst+"/files", include='*.*')
        self.xuff.copytree(src="pages/.well-known", dst=dst+"/.well-known", include="*")

    def do_copy_live(self):
        for xslt_file in glob.glob("*.xslt"):
            self.xuff.copyfile(src=xslt_file, dst=os.path.join(self.ROOT, xslt_file))

    def do_collectstatic(self):
        call_command('collectstatic', interactive=False)

    def do_timestamps(self):
        with open(os.path.join(self.ROOT, "djstell/settings_timestamp.py"), "w") as f:
            print(f"DEPLOY_TIME = '{int(time.time())}'", file=f)

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
        if os.path.exists(self.ROOT):
            shutil.rmtree(self.ROOT)
        if os.path.exists(self.VERB_ROOT):
            shutil.rmtree(self.VERB_ROOT)

    @timed
    def do_load(self):
        call_command('migrate', verbosity=False, interactive=False)
        loadpages.load_all()
        if self.user_data:
            call_command('loaddata', self.user_data)

    def do_1blog(self):
        loadpages.blog_sources = ['1blog']

    def do_narrow(self):
        """Total hack expedient to only process some blog posts."""
        # Change this pattern if you want to fiddle with another one.
        loadpages.blog_pattern = "*github*.bx"

    def only_some(self, word):
        loadpages.blog_pattern = "*{}*.bx".format(word)
        loadpages.page_pattern = "*{}*.px".format(word)

    def do_pnarrow(self):
        """Total hack expedient to only process some pages."""
        # Change this pattern if you want to fiddle with another one.
        loadpages.page_pattern = "*xx*.px"

    @timed
    def do_make(self):
        self.generate(self.ROOT)
        self.do_copy_verbatim()
        self.do_support()

    @timed
    def do_support(self):
        for sassfile in glob.glob("style/[a-z]*.scss"):
            self.run_sass(sassfile, self.VERB_ROOT)
        for here, there in self.COPY_FILES:
            self.xuff.copyfile(here, os.path.join(self.ROOT, there))
        for here, there in self.COPY_TREES:
            self.xuff.copytree(src=here, dst=os.path.join(self.ROOT, there), include="*.*")

        # Build the JS file as the concatenation of others.
        with open("js/ingredients.txt") as ingredients:
            js = ingredients.read().split()
        with open(self.VERB_ROOT+"/nedbatchelder.js", "w") as outjs:
            for f in js:
                with open("js/"+f) as jsin:
                    outjs.write(jsin.read())
                outjs.write("\n")

    def do_djstell(self):
        self.xuff.copytree(src='djstell', dst=os.path.join(self.ROOT, "djstell"), include='*.*')

    @timed
    def do_upload(self):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s", "%H:%M:%S"))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)
        self.xuff.upload(**self.FTP)

    @timed
    def do_rsyncdb(self):
        run_cmd("rsync", "-arvz", f"{self.ROOT}/djstell/stell.db", f"{self.RSYNC_DST}/djstell")

    def do_restart(self):
        run_cmd("ssh", self.server, "systemctl", "--user", "restart", self.slug)
        run_cmd("ssh", self.server, "systemctl", "--user", "status", self.slug)

    def do_all(self):
        self.exec_words(self.all_words.split())

    def exec_words(self, argv):
        for word in argv:
            if word.startswith("only_"):
                self.only_some(word[5:])
                continue
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
