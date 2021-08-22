import os

from .settings import *

BASE = 'http://127.0.0.1:8000'
EXT_BASE = BASE
PHP = False
AS_PHP = False

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJSTELL / "stell.db",
    }
}

STATIC_URL = "/"
STATICFILES_DIRS = [
    (DJSTELL / "../live").resolve(),
]

SENDFILE_BACKEND = "sendfile.backends.development"
