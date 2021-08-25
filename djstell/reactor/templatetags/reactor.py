from django import template

from ..models import Comment
from ..honey import Honeypotter

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


@register.inclusion_tag("comments.html", takes_context=True)
def entry_comments(context, entryid, url):
    comments = Comment.objects.filter(entryid=entryid).order_by("posted")
    hp = Honeypotter(context["request"], entryid)
    hp.new()
    context = {
        "comments": comments,
        "entryid": entryid,
        "url": url,
    }
    context.update(hp.context_data())
    return context
