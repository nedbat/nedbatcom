# Based on https://help.dreamhost.com/hc/en-us/articles/360002341572-Creating-a-Django-project
# Must be Python 2 compatible.

from __future__ import print_function

import sys, os

VENV = "/home/nedbat/venvs/nednet"
LOG = "/home/nedbat/passlog.txt"

INTERP = VENV + "/bin/python3"

if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

try:
    sys.path.append(os.getcwd())
    os.environ['DJANGO_SETTINGS_MODULE'] = "djstell.settings_nednet"

    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as ex:
    with open(LOG, "a") as f:
        import traceback
        traceback.print_exc(file=f)
