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
        'TEST': {
            'NAME': DJSTELL / "stell.db",
        },
    },
    'reactor': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJSTELL / "reactor.db",
    },
}

STATIC_URL = "/"
STATICFILES_DIRS = [
    DJSTELL.parent,
]

SENDFILE_BACKEND = "django_sendfile.backends.development"
SENDFILE_ROOT = DJSTELL.parent
