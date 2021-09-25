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
