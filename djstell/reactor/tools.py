import hashlib


def md5(*parts):
    text = "".join(str(p or "") for p in parts)
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def get_client_ip(request):
    x_forwarded_for = request.headers.get('x-forwarded-for')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
