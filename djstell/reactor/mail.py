from django.conf import settings
from django.core import mail as django_mail
from django.template.loader import render_to_string

from .models import Comment

def send_owner_email(com, markdown_body, context):
    context["comment"] = com
    context["for_admin"] = True
    context["markdown_body"] = markdown_body
    context["watcher_emails"] = watcher_emails(com)
    subject = f'A comment on "{context["title"]}" from {com.name}'
    body = render_to_string("notify_email.txt", context)
    django_mail.send_mail(
        subject=subject,
        message=body,
        from_email=settings.REACTOR_FROM_EMAIL,
        recipient_list=[settings.REACTOR_ADMIN_EMAIL],
        fail_silently=False,
    )

def watcher_emails(com):
    watchers = Comment.objects.filter(entryid=com.entryid, notify=True)
    watch_emails = set(c.email for c in watchers if c.email != com.email)
    return sorted(watch_emails)

def send_watcher_emails(com, markdown_body, context):
    watch_emails = watcher_emails(com)
    context["comment"] = com
    context["markdown_body"] = markdown_body
    context["for_admin"] = False
    subject = f'[{settings.SITE_NAME}] A comment on "{context["title"]}" from {com.name}'
    body = render_to_string("notify_email.txt", context)
    html = render_to_string("notify_email.html", context)
    for wemail in watch_emails:
        django_mail.send_mail(
            subject=subject,
            message=body,
            html_message=html,
            from_email=settings.REACTOR_FROM_EMAIL,
            recipient_list=[wemail],
            fail_silently=False,
        )
