# Based on https://help.dreamhost.com/hc/en-us/articles/360002341572-Creating-a-Django-project
# Must be Python 2 compatible.

from __future__ import print_function

import sys, os

VENV = "/home/nedbat/venvs/nednet"
INTERP = VENV + "/bin/python3"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

LOG = "/home/nedbat/passlog.txt"

try:
    cwd = os.getcwd()
    sys.path.append(cwd)
    #sys.path.append(cwd + "/djstell")

    # sys.path.insert(0, VENV + "/bin")
    # sys.path.insert(0, VENV + "/lib/python3.7/site-packages")

    # with open(LOG, "a") as f:
    #     print("Passenger running, pid={}".format(os.getpid()), file=f)
    #     print("sys.executable = {}".format(sys.executable), file=f)
    #     print("\n".join(sys.path), file=f)

    os.environ['DJANGO_SETTINGS_MODULE'] = "djstell.settings_nednet"

    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as ex:
    with open(LOG, "a") as f:
        import traceback
        traceback.print_exc(file=f)
