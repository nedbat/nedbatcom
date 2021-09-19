import os

from .settings import *

BASE = '//nedbatchelder.com'
EXT_BASE = f'https:{BASE}'

SITE_NAME = "nedbatchelder.com"

PHP = False
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["nedbatchelder.com"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJSTELL / "stell.db",
    },
}

STATIC_URL = "/"
STATICFILES_DIRS = []
STATIC_ROOT = (DJSTELL / "../live/public").resolve()
