import os

from .settings import *

BASE = '//nedbatchelder.net'
EXT_BASE = f'https:{BASE}'

SITE_NAME = "nedbatchelder.net"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["nedbatchelder.net"]
CSRF_TRUSTED_ORIGINS = ["https://nedbatchelder.net"]

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
