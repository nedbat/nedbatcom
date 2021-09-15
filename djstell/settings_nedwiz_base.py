import os

from .settings import *

BASE = '//uwsgi.nedbatchelder.net'
EXT_BASE = f'https:{BASE}'

SITE_NAME = "uwsgi.nedbatchelder.net"

PHP = False
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["uwsgi.nedbatchelder.net"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJSTELL / "stell.db",
    },
}

STATIC_URL = "/"
STATICFILES_DIRS = [
    DJSTELL.parent,
]
