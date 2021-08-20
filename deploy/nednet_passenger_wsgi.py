# Based on https://help.dreamhost.com/hc/en-us/articles/360002341572-Creating-a-Django-project

import sys, os
INTERP = "/home/nedbat/venvs/nednet/bin/python3"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + '/djangoprojectname')  #You must add your project here

sys.path.insert(0,cwd+'/venv/bin')
sys.path.insert(0,cwd+'/venv/lib/python3.8/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = "djangoprojectname.settings"
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
