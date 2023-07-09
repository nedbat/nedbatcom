import datetime
import re
import time
import urllib.parse

def datetime_from_8601(s8601):
    return datetime.datetime(*time.strptime(s8601, "%Y%m%dT%H%M%S")[:6])

def id_from_text(s):
    s = urllib.parse.quote(s.strip().replace(' ', '_').encode('utf-8'))
    return s.replace('%', '_')

def slug_from_text(txt):
    # Normalize spaces.
    txt = re.sub(r"\s+", " ", txt)
    # Only ascii characters, _ for space, and lowercase.
    slug = txt.encode('ascii', 'ignore').decode('ascii').replace(' ', '_').lower()
    # Nothing other than word characters
    slug = re.sub(r'[^\w _]', r'', slug)
    # No double underscores.
    slug = re.sub(r'_+', r'_', slug)
    # No underscores at the ends.
    slug = slug.strip(' _')
    # If nothing is left, do something really geeky.
    if not slug:
        slug = id_from_text(txt)
    # Limit to a reasonable size
    maxlen = 60
    if len(slug) > maxlen:
        clip = slug[:maxlen].rfind('_')
        if clip > 0:
            slug = slug[:clip]
    return slug


NUMBER_NAMES = dict(enumerate(
    "zero one two three four five six seven eight nine ten".split()
))

def years_age(age):
    years, frac = divmod(age.days / 365.25, 1)
    years = int(years)
    if frac < 1/365:
        modifier = "exactly "
    elif frac < 2/12:
        modifier = ""
    elif frac < 4/12:
        modifier = "more than "
    elif frac < 8/12:
        modifier = "over "
    elif frac < 9/12:
        modifier = "close to "
        years += 1
    elif frac < 10/12:
        modifier = "almost "
        years += 1
    elif frac < 11/12:
        modifier = "nearly "
        years += 1
    elif frac < 364/365:
        modifier = ""
        years += 1
    else:
        modifier = "exactly "
        years += 1
    years = NUMBER_NAMES.get(years, years)
    return f"{modifier}{years} years"
