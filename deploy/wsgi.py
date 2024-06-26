"""
Generic Django wsgi connector.

Define DJANGO_SETTINGS_MODULE in the environment.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
