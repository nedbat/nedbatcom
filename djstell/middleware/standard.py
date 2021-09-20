""" Helpful middleware!
"""

from django.utils.deprecation import MiddlewareMixin

class AnnounceErrorsMiddleware(MiddlewareMixin):
    """ Make sure exceptions get mentioned on stdout, for use while generating
        static pages.
    """
    def process_exception(self, request, exception):
        print(ascii("Error: %s -> %s" % (request.path, exception)))
