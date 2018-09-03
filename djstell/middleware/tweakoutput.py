""" Post-process the HTML.
"""

# PT.Serif has weird quotes that we fix with CSS.

REPLACEMENTS = [
    ('&#8220;', '<span class="oq">&#8220;</span>'),
    ('&#8221;', '<span class="cq">&#8221;</span>'),
    ('&#8216;', '<span class="oq">&#8216;</span>'),
    ('&#8217;', '<span class="cq">&#8217;</span>'),
]

class TweakOutputMiddleware:
    def process_response(self, request, response):
        for before, after in REPLACEMENTS:
            response.content = response.content.replace(before, after)
        return response
