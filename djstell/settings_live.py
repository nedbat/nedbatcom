import os

from .settings import *

BASE = 'http://127.0.0.1:8000'
EXT_BASE = BASE

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(DJSTELL / "stell.db"),
    }
}

STATIC_URL = "/"
STATICFILES_DIRS = [
    str((DJSTELL / "../live").resolve()),
]

SENDFILE_BACKEND = "sendfile.backends.development"
