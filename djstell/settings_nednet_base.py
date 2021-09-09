import os

from .settings import *

BASE = '//nedbatchelder.net'
EXT_BASE = f'https:{BASE}'

PHP = False
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["nedbatchelder.net"]

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
