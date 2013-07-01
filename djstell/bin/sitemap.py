import cPickle as pickle
import re

host = 'http://nedbatchelder.com/'

re_ext = re.compile("|".join([ '\\.'+e+'$' for e in 'html jpg png gif xml py'.split()]))

mdict = pickle.load(open("totalchoice.md5"))
urls = mdict.keys()
urls.sort()
sitemapfile = open('sitemap.txt', 'w')
for url in urls:
    if re_ext.search(url):
        sitemapfile.write(host + url.replace('\\', '/') + '\n')
