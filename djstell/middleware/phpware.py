""" Run the output of Django through PHP!
"""

import shlex, subprocess
from io import StringIO
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class PhpMiddleware(MiddlewareMixin):

    if settings.PHP:
        def process_response(self, request, response):
            cmd = "php -- "
            proc = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.stdin.write(response.content)
            proc.stdin.close()
            response.content = proc.stdout.read()
            err = proc.stderr.read()
            if err:
                response.content = response.content.replace('</body>', '<pre>' + err + '</pre></body>')
            return response
