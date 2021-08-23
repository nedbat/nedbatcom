from django.conf import settings
from django import template

from djstell.reactor.models import Comment

register = template.Library()


@register.simple_tag
def comment_label(entryid):
    num = Comment.objects.filter(entryid=entryid).count()
    if num == 0:
        return "react"
    elif num == 1:
        return "1 reaction"
    else:
        return f"{num} reactions"


@register.inclusion_tag("comments.html")
def entry_comments(entryid):
    comments = Comment.objects.filter(entryid=entryid).order_by("posted")
    return {
        "comments": comments,
    }
