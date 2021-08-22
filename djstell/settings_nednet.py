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
        'NAME': DJSTELL / "stell.db",
    }
}

STATIC_URL = "/"
STATICFILES_DIRS = [
    DJSTELL.parent,
]

# xsendfile works on dreamhost if you ask support to enable it for your domain.
SENDFILE_BACKEND = "sendfile.backends.xsendfile"
