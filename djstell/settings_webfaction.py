from .settings import *

WEB_ROOT = "html"
SERVER_NAME = "nedbatchelder.com"
BASE = f"//{SERVER_NAME}"
EXT_BASE = f"https://{SERVER_NAME}"
WWWROOT = "/home/nedbat/webapps/main"
PHP = False
AS_PHP = True
PHP_INCLUDE = True
ALLOWED_HOSTS = [SERVER_NAME]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJSTELL / "stell.db",
    },
}
