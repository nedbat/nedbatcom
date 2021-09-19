import os

from .settings import *

BASE = '//nedbatchelder.net'
EXT_BASE = f'https:{BASE}'

SITE_NAME = "nedbatchelder.net"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["nedbatchelder.net"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJSTELL / "stell.db",
    },
}

STATIC_URL = "/"
STATICFILES_DIRS = []
STATIC_ROOT = (DJSTELL / "../live/public").resolve()
