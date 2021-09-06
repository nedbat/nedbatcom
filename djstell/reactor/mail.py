from django.conf import settings
from django.core import mail as django_mail

from .models import Comment

def send_owner_email(com):
    django_mail.send_mail(
        subject="Someone commented",
        message="THE BODY",
        from_email=settings.REACTOR_FROM_EMAIL,
        recipient_list=[settings.REACTOR_ADMIN_EMAIL],
        fail_silently=False,
    )

def send_watcher_emails(com):
    watchers = Comment.objects.filter(entryid=com.entryid, notify=True)
    watch_emails = set(c.email for c in watchers if c.email != com.email)
    subject = "A comment on BLAH"
    body = "HERE IS THE BODY"
    messages = [
        (subject, body, settings.REACTOR_FROM_EMAIL, [wemail])
        for wemail in watch_emails
    ]
    if messages:
        django_mail.send_mass_mail(messages, fail_silently=False)
