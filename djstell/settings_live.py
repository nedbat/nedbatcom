import os

from .settings import *

BASE = 'http://127.0.0.1:8000'
EXT_BASE = BASE
LOCAL_LIVE = True

SITE_NAME = "nedlive.net"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

if bool(os.environ.get("LIVE_NODJTB", "")):
    INTERNAL_IPS = []

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJSTELL / "stell.db",
        'TEST': {
            'NAME': DJSTELL / "stell.db",
        },
    },
    'reactor': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJSTELL / "reactor.db",
    },
}

STATIC_URL = "/live_static/"
STATICFILES_DIRS = [
    (DJSTELL / "../live/public").resolve(),
]
MY_BOGUS_STATIC_DIR = "live/public"

SENDFILE_BACKEND = "django_sendfile.backends.development"
SENDFILE_ROOT = DJSTELL.parent

# For tests and development, no site caching.
CACHE_MIDDLEWARE_SECONDS = 0
