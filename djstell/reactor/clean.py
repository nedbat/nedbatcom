import functools

import bleach
import markdown2


TLDS = bleach.linkifier.TLDS[:]
TLDS.remove("py")
TLDS.remove("rs")

URL_RE = bleach.linkifier.build_url_re(tlds=TLDS)

MARKDOWN_EXTRAS = ["fenced-code-blocks", "cuddled-lists", "code-friendly", "smarty-pants"]

def convert_body(body):
    """
    Convert the body of a submitted comment into clean HTML.
    """
    body = body.strip()
    if not body:
        # Empty markdown becomes "<p></p>" which just complicates things.
        return ""
    html = markdown2.markdown(body, extras=MARKDOWN_EXTRAS)
    linkifier = functools.partial(
        bleach.linkifier.LinkifyFilter,
        skip_tags=['pre'],
        url_re=URL_RE,
    )
    cleaner = bleach.sanitizer.Cleaner(
        tags=["a", "b", "i", "em", "strong", "ul", "ol", "li", "p", "br", "pre", "code"],
        styles=[],
        strip=True,
        strip_comments=True,
        filters=[linkifier],
    )

    html = cleaner.clean(html).strip()
    return html
