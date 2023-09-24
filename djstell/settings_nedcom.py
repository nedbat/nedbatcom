import os

from .settings_nedcom_base import *
from .settings_nedcom_db import *

ANALYTICS = True

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

# Email settings
#   https://docs.djangoproject.com/en/3.2/topics/email/#smtp-backend
#   https://www.dreamhost.com/blog/how-to-fix-wordpress-not-sending-email/
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 30
EMAIL_HOST_USER = 'nedbat@gmail.com'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

SESSION_FILE_PATH = "/home/nedbat/var/session_nedcom"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/home/nedbat/var/cache_nedcom',
        'KEY_PREFIX': DEPLOY_TIME,
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
    },
}
