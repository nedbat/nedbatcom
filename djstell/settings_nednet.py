import os

from .settings import *

BASE = '//nedbatchelder.net'
EXT_BASE = BASE

PHP = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["nedbatchelder.net"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJSTELL / "stell.db",
    },
    'reactor': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nednet_reactor',
        'USER': 'nednet_reactor',
        'PASSWORD': os.environ.get('REACTOR_PASSWORD'),
        'HOST': 'mysql2.nedbatchelder.net',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_ALL_TABLES'",
        },
    },
}

STATIC_URL = "/"
STATICFILES_DIRS = [
    DJSTELL.parent,
]

# xsendfile works on dreamhost if you ask support to enable it for your domain.
SENDFILE_BACKEND = "sendfile.backends.xsendfile"
