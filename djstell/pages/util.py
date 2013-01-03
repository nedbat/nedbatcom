import datetime, re, time, urllib

def datetime_from_8601(s8601):
    return datetime.datetime(*time.strptime(s8601, "%Y%m%dT%H%M%S")[:6])

def id_from_text(s):
    s = urllib.quote(s.strip().replace(' ', '_').encode('utf-8'))
    return s.replace('%', '_')

def slug_from_text(txt):
    # Only ascii characters, _ for space, and lowercase.
    slug = txt.encode('ascii', 'ignore').replace(' ', '_').lower()
    # Nothing other than word characters
    slug = re.sub('[^\w _]', '', slug)
    # No double underscores.
    slug = re.sub('_+', '_', slug)
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
