import os

from .settings_nedcom_base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJSTELL / "stell.db",
    },
    'reactor': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nedcom_reactor',
        'USER': 'nedcom_reactor',
        'PASSWORD': os.environ.get('REACTOR_PASSWORD'),
        'HOST': 'mysql2.nedbatchelder.net',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_ALL_TABLES'",
        },
    },
}

# xsendfile works on dreamhost if you ask support to enable it for your domain.
SENDFILE_BACKEND = "django_sendfile.backends.simple"
SENDFILE_ROOT = DJSTELL.parent

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/nedbat/djlog_nedcom.txt',
            'formatter': 'standard',
        },
    },
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s %(name)s] %(filename)s:%(lineno)d: %(message)s',
        },
        'raw': {
            'format': '%(message)s'
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
