import os

from .settings import *

BASE = '//nedbatchelder.net'
EXT_BASE = BASE

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

SENDFILE_BACKEND = "sendfile.backends.development"
