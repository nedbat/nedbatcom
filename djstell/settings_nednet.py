import os

from .settings import *

BASE = '//nedbatchelder.net'
EXT_BASE = BASE

PHP = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["nedbatchelder.net"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': mybase + "stell.db",
    }
}

STATIC_URL = "/"
STATICFILES_DIRS = [
    os.path.abspath(mybase + ".."),
]

# Tried other backends, without extra settings:
#   Backends that did work: development, simple (with DEBUG=True)
#   Backends that didn't work: xsendfile, mod_wsgi, nginx
SENDFILE_BACKEND = "sendfile.backends.simple"
