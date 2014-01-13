# Context processors.

from django.conf import settings

def doit(request):
    """ Put settings into the context as 'settings'
    """
    return {
        'settings': settings,
    }
