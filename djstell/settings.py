# Django settings for djstell project.

import os
from pathlib import Path

# Read .env
# It should have:
#   REACTOR_PASSWORD=xyzzy
#   SECRET_KEY=xyzzy

import dotenv
dotenv.load_dotenv()

PHP = True              # Should we execute PHP tags in the output?
PHP_INCLUDE = False     # Should we use PHP includes, or pull the content in?
AS_PHP = False

BASE = 'http://localhost/'
LOG_SQL = False

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

REACTOR_FROM_EMAIL = "reactor@nedbatchelder.com"
REACTOR_ADMIN_EMAIL = "ned@nedbatchelder.com"

SITE_NAME = "nedbatchelder.com"

DJSTELL = Path(__file__).resolve().parent

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DATABASE_ROUTERS = ['djstell.reactor.models.ReactorRouter']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = None

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = None

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

STATIC_URL = "/"
MY_BOGUS_STATIC_DIR = ""

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get("SECRET_KEY", "doesn't matter")

CONN_MAX_AGE = None

MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'djstell.middleware.phpware.PhpMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'djstell.middleware.standard.AnnounceErrorsMiddleware',
    'djstell.middleware.standard.LogQueriesMiddleware',
)

ROOT_URLCONF = 'djstell.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            DJSTELL / 'pages/templates',
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'djstell.middleware.context_processors.inject_settings',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django_sendfile',
    'djstell.pages',
    'djstell.reactor',
    'debug_toolbar',
)

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

INTERNAL_IPS = [
    '127.0.0.1',
    # For debug-toolbar on remote servers:
    # '71.232.43.199',
]
