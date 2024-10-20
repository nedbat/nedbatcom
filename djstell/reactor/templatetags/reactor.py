import copy

from django import template

from ..models import Comment
from ..honey import CommentForm

register = template.Library()


@register.simple_tag
def comment_label(entryid):
    num = Comment.objects.filter(entryid=entryid).count()
    if num == 0:
        return "react"
    elif num == 1:
        return "1\xa0reaction"
    else:
        return f"{num}\xa0reactions"


@register.inclusion_tag("comments.html", takes_context=True)
def entry_comments(context, entryid, url, closed):
    form = CommentForm(context["request"], entryid)
    context = copy.copy(context)

    if form.is_post and not closed:
        form.handle_post(context)
        if form.is_adding and form.is_ok():
            # We finished a successful post, the view function should redirect.
            context["should_redirect"][0] = True

    comments = Comment.objects.filter(entryid=entryid).order_by("posted")
    context.update({
        "comments": comments,
        "url": url,
        "closed": closed,
    })
    context.update(form.context_data())
    return context
