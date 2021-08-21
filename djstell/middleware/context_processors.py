# Context processors.

from django.conf import settings

def inject_settings(request):
    """ Put settings into the context as 'settings'
    """
    return {
        'settings': settings,
    }
