from django.conf import settings
from django import template

from djstell.reactor.models import Comment

register = template.Library()

@register.inclusion_tag("comments.html")
def entry_comments(entryid):
    comments = Comment.objects.filter(entryid=entryid).order_by("posted")
    return {
        "comments": comments,
        "entryid": entryid,
    }
