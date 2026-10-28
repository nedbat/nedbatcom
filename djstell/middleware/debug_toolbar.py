# Debug toolbar helpers.

from django.conf import settings

def show_toolbar_behind_proxy(request):
    """ Decide whether to show the debug toolbar when running behind a proxy.

    The proxy makes REMOTE_ADDR useless, so use X-Forwarded-For instead.  Only
    the last entry is trustworthy: it was added by the proxy, while earlier
    entries come from the client and can be forged.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if not forwarded:
        return False
    client_ip = forwarded.split(",")[-1].strip()
    return client_ip in settings.INTERNAL_IPS
