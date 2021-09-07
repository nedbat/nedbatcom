import datetime

from django.core import mail
import pytest

from ..mail import send_owner_email, send_watcher_emails
from ..models import Comment


def make_comment(
    name,
    email,
    website="https://myweb.com",
    notify=False,
    entryid="123",
    posted=datetime.datetime(2021, 9, 1),
    ):
    return Comment(
        entryid=entryid,
        name=name,
        email=email,
        notify=notify,
        website=website,
        posted=posted,
    )


@pytest.mark.django_db(databases=['reactor'])
class TestEmail:
    def test_one_notification(self):
        make_comment(name="Tom", email="tom@tom.com", notify=True).save()
        com = make_comment(name="Nik", email="nik@nik.com")
        send_watcher_emails(com, {"title": "My Blog Post"})
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == f'A comment on "My Blog Post" from Nik'
        assert mail.outbox[0].recipients() == ["tom@tom.com"]

    def test_two_notifications(self):
        # Two comments mean two emails get sent.
        make_comment(name="Tom", email="tom@tom.com", notify=True).save()
        make_comment(name="Nik", email="nik@nik.com", notify=True).save()
        com = make_comment(name="Jo", email="jo@anne.com")
        send_watcher_emails(com, {"title": "My Blog Post"})
        assert len(mail.outbox) == 2
        assert mail.outbox[0].subject == f'A comment on "My Blog Post" from Jo'
        assert mail.outbox[0].recipients() == ["nik@nik.com"]
        assert mail.outbox[1].subject == f'A comment on "My Blog Post" from Jo'
        assert mail.outbox[1].recipients() == ["tom@tom.com"]

    def test_no_duplicates(self):
        # Two comments from the same person, but they only get one email.
        make_comment(name="Tom", email="tom@tom.com", notify=True).save()
        make_comment(name="Nik", email="nik@nik.com", notify=True).save()
        make_comment(name="Nik", email="nik@nik.com", notify=True).save()
        com = make_comment(name="Jo", email="jo@anne.com")
        send_watcher_emails(com, {"title": "My Blog Post"})
        assert len(mail.outbox) == 2
        assert mail.outbox[0].subject == f'A comment on "My Blog Post" from Jo'
        assert mail.outbox[0].recipients() == ["nik@nik.com"]
        assert mail.outbox[1].subject == f'A comment on "My Blog Post" from Jo'
        assert mail.outbox[1].recipients() == ["tom@tom.com"]

    def test_notifications_only_from_the_same_post(self):
        # Notifications for one post don't get confused about other posts.
        make_comment(entryid="123", name="Tom", email="tom@tom.com", notify=True).save()
        make_comment(entryid="123", name="Nik", email="nik@nik.com", notify=True).save()
        make_comment(entryid="456", name="Sue", email="sue@sue.com", notify=True).save()
        com = make_comment(entryid="456", name="Jo", email="jo@anne.com")
        send_watcher_emails(com, {"title": "Another Blog Post"})
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == f'A comment on "Another Blog Post" from Jo'
        assert mail.outbox[0].recipients() == ["sue@sue.com"]
