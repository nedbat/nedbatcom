import os

from .settings import *

BASE = '//nedbatchelder.com'
EXT_BASE = f'https:{BASE}'

SITE_NAME = "nedbatchelder.com"
NOINDEX = False

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
# collectstatic needs to put files here:
STATIC_ROOT = (DJSTELL / "../to_dh/public").resolve()
