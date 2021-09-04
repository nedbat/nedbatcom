import functools

import bleach


TLDS = bleach.linkifier.TLDS[:]
TLDS.remove("py")
TLDS.remove("rs")

URL_RE = bleach.linkifier.build_url_re(tlds=TLDS)

def clean_html(html):
    linkifier = functools.partial(
        bleach.linkifier.LinkifyFilter,
        skip_tags=['pre'],
        url_re=URL_RE,
    )
    cleaner = bleach.sanitizer.Cleaner(
        tags=["a", "b", "i", "p", "br", "pre"],
        styles=[],
        strip=True,
        strip_comments=True,
        filters=[linkifier],
    )

    return cleaner.clean(html)
