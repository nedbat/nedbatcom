""" Helpful middleware!
"""

from pathlib import Path

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.views.static import serve

class AnnounceErrorsMiddleware(MiddlewareMixin):
    """ Make sure exceptions get mentioned on stdout, for use while generating
        static pages.
    """
    def process_exception(self, request, exception):
        print(ascii("Error: %s -> %s" % (request.path, exception)))

class StaticOverlayMiddleware(MiddlewareMixin):
    """ Serve static files if they exist, otherwise let Django handle it.
    """
    if settings.LOCAL_LIVE:
        def process_request(self, request):
            path = request.path.lstrip("/")
            file_maybe = Path(settings.MY_BOGUS_STATIC_DIR) / path
            if file_maybe.is_file():
                return serve(request, path=path, document_root=settings.MY_BOGUS_STATIC_DIR)
            return None
