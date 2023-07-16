from pathlib import Path

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django_sendfile import sendfile
from PIL import Image

import logging
logger = logging.getLogger(__name__)

def imgvar(request, var, path):
    """
    Convert an image on-demand.
    The file is saved back where Apache will find it, so we only ever get one
    request per picture.
    """
    if var == "webp":
        inpath = path.removesuffix(".webp")
        saveas = "WEBP"
    else:
        raise Http404(f"No such {var=}")

    static_root = Path(settings.STATIC_ROOT)
    outpath = static_root / "iv" / var / path

    try:
        im = Image.open(static_root / inpath)
    except:
        raise Http404(f"Couldn't find {path=}")

    outpath.parent.mkdir(parents=True, exist_ok=True)
    if inpath.endswith(".jpg"):
        options = dict(lossless=False, quality=50, method=6)
    elif path.endswith(".png"):
        options = dict(lossless=True, quality=80, method=6)
    else:
        options = {}
    im.save(outpath, saveas, **options)
    return sendfile(request, outpath)
