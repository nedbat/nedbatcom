import os

from .settings_nednet_base import *

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

# xsendfile works on dreamhost if you ask support to enable it for your domain.
SENDFILE_BACKEND = "django_sendfile.backends.xsendfile"
SENDFILE_ROOT = DJSTELL.parent

# when serving, we find files here:
STATIC_ROOT = (DJSTELL / "../public").resolve()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/nedbat/djlog_nednet.txt',
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

# Email settings
#   https://docs.djangoproject.com/en/3.2/topics/email/#smtp-backend
#   https://www.dreamhost.com/blog/how-to-fix-wordpress-not-sending-email/
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.dreamhost.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ned@nedbatchelder.net'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/home/nedbat/var/cache_nednet',
        'KEY_PREFIX': DEPLOY_TIME,
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}
