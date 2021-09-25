""" Helpful middleware!
"""

from pathlib import Path

from django.conf import settings
from django.shortcuts import redirect
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

    This is just for local debugging, instead of having to run Apache.
    """
    if settings.LOCAL_LIVE:
        def process_request(self, request):
            def serve_file(path):
                return serve(request, path=path, document_root=settings.MY_BOGUS_STATIC_DIR)

            rpath = request.path
            path = rpath.lstrip("/")
            file_maybe = Path(settings.MY_BOGUS_STATIC_DIR) / path
            if file_maybe.is_file():
                # Path is an actual static file: serve it.
                return serve_file(path)
            elif file_maybe.is_dir():
                if not rpath.endswith("/"):
                    # Path is a directory, but we need it to end with slash, redirect.
                    return redirect(rpath + "/")
                index_html = file_maybe / "index.html"
                if index_html.is_file():
                    # A directory with an index.html, serve it.
                    return serve_file(path + "/index.html")

            # Django will get the request.
            return None
