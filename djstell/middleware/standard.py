""" Helpful middleware!
"""

from django.db import connection
from django.conf import settings
from textwrap import TextWrapper
import datetime, os, re, sys

class AnnounceErrorsMiddleware:
    """ Make sure exceptions get mentioned on stdout, for use while generating
        static pages.
    """
    def process_exception(self, request, exception):
        print "Error: %s -> %s" % (request.path, exception)

wrapper = TextWrapper(subsequent_indent=' '*9, width=159)
table_name_re = re.compile(r'FROM (?P<table_name>[^ ]+) *(WHERE|$)')
simple_select_clause_re = re.compile(r'SELECT [^().]*,[^().]* FROM')

def print_queries(showsql=1, outfile=sys.stdout):
    """ Print the Django db.queries list as nicely as possible.
    """
    q_len = len(connection.queries)
    if showsql and q_len >= showsql:
        for d in connection.queries:
            sql = d['sql']
            # Get rid of the table name if it is a single-table query.
            match = table_name_re.search(sql)
            if match:
                sql = sql.replace(match.groupdict()['table_name']+'.', '')

            sql = simple_select_clause_re.sub('SELECT *** FROM', sql)

            # Everything is quoted with backticks, and the commas have no space.
            # Fix those things too.
            sql = sql.replace('`', '').replace(',', ', ')
            for l in wrapper.wrap("%s: %s" % (d['time'], sql)):
                outfile.write('\t')
                outfile.write(l)
                outfile.write('\n')

class LogQueriesMiddleware:
    """ Log the queries for each path
    """
    
    if settings.LOG_SQL:
        def process_response(self, request, response):
            fp = file(os.path.join(r'c:\tmp', request.path.replace('/', '_')), 'a')
            fp.write('%s\n' % datetime.datetime.now())
            print_queries(True, fp)
            fp.close()
            return response
    
