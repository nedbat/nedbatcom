"""Base settings for nedbatchelder.com deployment."""

# This file is used as the settings while makehtml.py is run.
# See `env.%` in the Makefile.

from .settings import *

BASE = '//nedbatchelder.com'
EXT_BASE = f'https:{BASE}'

SITE_NAME = "nedbatchelder.com"
NOINDEX = False

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["nedbatchelder.com"]
CSRF_TRUSTED_ORIGINS = ["https://nedbatchelder.com"]

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
