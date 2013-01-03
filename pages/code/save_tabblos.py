"""Save Tabblos from tabblo.com"""

# Copyright 2012, Ned Batchelder.
# Released under the MIT license.

# Note: In this program we are scraping HTML with regexes.  Look at this: 
#    http://stackoverflow.com/questions/1732348/1732454#1732454
# It's funny!  But don't be dogmatic.  Scraping ids out of predictable
# well-understood HTML is a simple task for regexes.  When a beginner says, 
# "I need to parse HTML, I'm going to use regexes," and an expert answers, 
# "You shouldn't parse HTML with regexes," they are both confused.

import json, re, sys, time, urllib, urllib2, zipfile
import os, os.path
from cStringIO import StringIO
from contextlib import closing

MINE = "http://www.tabblo.com/studio/view/mine/"
NAVBAR = '<a class="navbarlinks" href="http://www.tabblo.com/studio/person/%s">Hi '

EXTRA_CSS_SPOT = "</style><script>"

EXTRA_CSS = """\
.grid_caption_main {
    display: block;
    position: absolute;
    z-index: 503;
}
.grid_caption_background {
    opacity: 0.8;    
    display: block;
    position: absolute;
    z-index: 502;
}
div.textblock p {
    margin: 0;
}
.parcel_holder {
    display: block;
    position: absolute;
}
.grid_textblock {
    display: block;
    position: absolute;
    z-index: 501;
}
p {
    margin-bottom: 0;
    margin-top: 1em;
}
"""

# build opener with HTTPCookieProcessor
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
urllib2.install_opener(opener)

class MyException(Exception):
    pass

class TabbloHarvester(object):
    """Harvest content from tabblo.com."""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.logged_in = False

    def open_url(self, url, verb="Reading", data=None, login=True):
        if login and not self.logged_in:
            # Visit /studio/login, don't need to do anything with the page, it will
            # set a cookie that future reads will use automatically.
            p = urllib.urlencode({ 'username': self.username, 'password': self.password })
            with closing(self.open_url('https://www.tabblo.com/studio/login/?s=1', "Logging in", p, login=False)) as f:
                content = f.read()
                # Why does tabblo.com not just return 302 for redirects??
                if '<meta http-equiv="Refresh" content="0; url=http://www.tabblo.com/studio/?pi=3">' in content:
                    with closing(self.open_url('http://www.tabblo.com/studio/?pi=3', login=False)) as f:
                        content = f.read()
                if (NAVBAR % self.username) not in content:
                    raise MyException("Couldn't log in.")
            self.logged_in = True

        print "%s: %s" % (verb, url)
        furl = opener.open(url, data)
        if furl.getcode() != 200:
            raise MyException("Bad status code from %s: %s" % (url, furl.getcode()))
        return furl

    def scrape_ids(self):
        """Get the tabblo ids from tabblo.com."""
        ids = []

        # Loop over all the pages of tabblos. 
        url = MINE
        while url:
            # Tabblo returns short pages sometimes!?
            for retry in range(10):
                with closing(self.open_url(url)) as f:
                    page = f.read()
                if page.rstrip().endswith("</html>"):
                    break
            else:
                raise MyException("Couldn't get a complete page, tried 10 times.")

            # Find tabblo ids by looking for a specific string in the URLs.
            for id in re.findall(r"javascript:Tabblo.site.deleteStory\((\d+),", page):
                ids.append(int(id))

            # Find the next page of tabblos.
            match = re.search(r'<a href="/studio/view/mine/(\d+)">More</a>', page)
            if match:
                url = MINE + match.group(1)
            else:
                url = None

        ids = list(reversed(ids))
        return ids

    def get_ids(self):
        """Get a list of all the tabblo ids for this account."""
        fname = "ids.txt"
        try:
            with open(fname) as ids_in:
                ids = [int(i) for i in ids_in.read().strip().split()]
        except IOError:
            # Couldn't read a stored list of ids, scrape them from the site,
            # and then save them in a file.
            ids = self.scrape_ids()

            # Write the ids to a text file, so if we need them again, we don't 
            # have to scrape them.
            with open(fname, "w") as ids_out:
                ids_out.write("".join("%d\n" % i for i in ids))

        return ids

    def download_tabblos(self, ids):
        """Download all the tabblos in the `ids` list."""
        for i, id in enumerate(ids, 1):
            n_of_m = "%s of %s" % (i, len(ids))
            for retry in range(3):
                try:
                    self.download_tabblo(id, n_of_m)
                    e = None
                    break
                except Exception, e:
                    print "Retrying..."
                    continue
            if e:
                raise e

    def download_tabblo(self, id, n_of_m):
        """Download a single tabblo.

        The tabblo id is `id`.  `n_of_m` is a string like "23 of 102".

        If the result directory already exists, we do nothing.

        """
        dname = "tabblo_%d" % id
        if os.path.exists(dname):
            # Looks like we already did this one.
            print "Already have #%d" % id
            return 

        url = "http://www.tabblo.com/studio/stories/zip/%d/?orig=1" % id
        verb = "Saving %s" % (n_of_m,)
        with closing(self.open_url(url, verb)) as fzip:
            zipdata = StringIO()
            zipdata.write(fzip.read())
            zipf = zipfile.ZipFile(zipdata)
            # The top level of the downloaded zipfile is tabblo_###, so we extract
            # to the current directory.
            zipf.extractall(".")
        
        # The HTML Tabblo serves could be a little better.
        with open(os.path.join(dname, "index.html")) as fhtml:
            html = fhtml.read()
        html = html.replace(EXTRA_CSS_SPOT, EXTRA_CSS + EXTRA_CSS_SPOT)
        with open(os.path.join(dname, "index.html"), "w") as fhtml:
            fhtml.write(html)

        # Unzipping leaves a confusing README.txt lying around, so delete it.
        try:
            os.remove("README.txt")
        except IOError:
            pass

    def generate_toc(self, ids):
        """Generate an HTML page to serve as the table of contents for `ids`."""
        # A dict mapping id to metadata for the tabblo.
        metadata = {}
        for id in ids:
            with open("tabblo_%d/metadata.json" % id) as fjson:
                md = json.load(fjson)
                md['date'] = time.strftime("%b %d, %Y", time.strptime(md['created'], "%Y-%m-%dT%H:%M:%S")).replace(" 0", " ")
                metadata[id] = md

        tocs = [
            # name          details     selector
            ('all',         True,       lambda md: True),
            ('published',   True,       lambda md: md['status'] == 'published'),
            ('public',      False,      lambda md: md['status'] == 'published' and md['access'] == 'public'),
            ]

        for name, details, selector in tocs:
            # A list of all the HTML chunks for the tabblos.
            tabblo_htmls = []
            for id in ids:
                md = metadata[id]
                if not selector(md):
                    continue
                if details:
                    deets = "%s, %s" % (md['status'], md['access'])
                else:
                    deets = ""
                tabblo_html = TABBLO_HTML % {
                    'title': escape_html(md['title']),
                    'imgsrc': "tabblo_%d/thumbnail.png" % id,
                    'link': "tabblo_%d/index.html" % id,
                    'date': md['date'],
                    'details': deets,
                }
                tabblo_htmls.append(tabblo_html)

            if tabblo_htmls:
                html = HTML % { 
                    'tabblos': "".join(tabblo_htmls),
                    'username': self.username,
                    }

                fname = "%s.html" % name
                print "Writing %s tabblos to %s" % (name, fname)
                with open(fname, "w") as ftoc:
                    ftoc.write(html.encode('ascii', 'xmlcharrefreplace'))

    def harvest_all_tabblos(self):
        """The big picture: read ids, download tabblos, and make a TOC."""
        print ("\n"
            "Saving tabblos by user %s.  This could take a long time.\n"
            "If it fails for some reason, just start it again, it will pick\n"
            "up where it left off.\n"
            % (self.username,)
            )

        ids = self.get_ids()
        print "%d tabblos" % len(ids)
        self.download_tabblos(ids)
        self.generate_toc(ids)


def escape_html(s):
    return (s
        .replace("&", "&amp;")
        .replace("'", "&#39;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        )

HTML = """\
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Tabblos by %(username)s</title>
<style>
html { font-family: verdana, helvetica, arial, sans-serif; padding: 2em; }
h1 { margin: 0em 0em 1em 0em; font-size: 24px; }
.tabblo { clear: both; padding: 1em 0em; }
.thumbnail { float: left; margin: 0em 2em 1em 0em; border: 1px solid #888; }
.title { margin: 0em; font-size: 18px; color: #039; }
.title a { text-decoration: none; }
.title a:hover { text-decoration: underline; }
.date { margin: 1em; font-size: 9px; }
.details { margin: 1em; font-size: 9px; color: #666; }
</style>
<body>
<h1>Tabblos by %(username)s</h1>
%(tabblos)s
</body>
</html>
"""

TABBLO_HTML = """\
<div class="tabblo">
    <a href="%(link)s">
        <img class="thumbnail" src="%(imgsrc)s">
    </a>
    <p class="title"><a href="%(link)s">%(title)s</a></p>
    <p class="date">%(date)s</p>
    <p class="details">%(details)s</p>
</div>
"""

if __name__ == '__main__':
    try:
        username, password = sys.argv[1:3]
    except:
        print "usage: %s USERNAME PASSWORD" % (sys.argv[0],)
    else:
        try:
            TabbloHarvester(username, password).harvest_all_tabblos()
        except MyException, e:
            print "\nUh-oh: %s" % e
