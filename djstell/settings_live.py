from .settings import *

BASE = 'http://127.0.0.1:8000'
EXT_BASE = BASE

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ["*"]

STATIC_URL = "/"
STATICFILES_DIRS = [
    mybase + "../live",
]

SENDFILE_BACKEND = "sendfile.backends.development"
