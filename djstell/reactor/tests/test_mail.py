import datetime

from django.core import mail
import pytest

from ..mail import send_owner_email, send_watcher_emails
from ..models import Comment


def make_comment(
    name,
    email,
    website="",
    notify=False,
    entryid="entry123",
    posted=datetime.datetime(2021, 9, 1),
    body="The Comment",
    ):
    return Comment(
        entryid=entryid,
        name=name,
        email=email,
        notify=notify,
        website=website,
        posted=posted,
        body=body,
    )


@pytest.mark.django_db(databases=['reactor'])
class TestEmail:
    def test_one_notification(self):
        make_comment(name="Tom", email="tom@tom.com", notify=True).save()
        com = make_comment(name="Nik", email="nik@nik.com", website="https://myweb.com", body="This is really great!")
        send_args = dict(
            com=com,
            markdown_body="This is really great!",
            context={
                "title": "My Blog Post",
                "url": "http://blog.com/123",
            },
        )
        send_owner_email(**send_args)
        send_watcher_emails(**send_args)
        assert len(mail.outbox) == 2

        owner_email = mail.outbox[0]
        assert owner_email.subject == 'A comment on "My Blog Post" from Nik'
        assert owner_email.recipients() == ["ned@nedbatchelder.com"]
        assert "\nhttp://blog.com/123\n" in owner_email.body
        assert "\nentryid: entry123\n" in owner_email.body
        assert "\nnotifications to: tom@tom.com\n" in owner_email.body

        email = mail.outbox[1]
        assert email.subject == f'[nedlive.net] A comment on "My Blog Post" from Nik'
        assert email.recipients() == ["tom@tom.com"]
        assert "\nhttp://blog.com/123\n" in email.body
        assert "\nname: Nik\n" in email.body
        assert "\nwebsite: https://myweb.com\n" in email.body
        assert "\nThis is really great!\n" in email.body
        assert "To unsubscribe" in email.body

        assert len(email.alternatives) == 1
        assert email.alternatives[0][1] == "text/html"
        html = email.alternatives[0][0]
        assert '<p>A comment on <a href="http://blog.com/123">My Blog Post</a> by' in html
        assert '<a href="https://myweb.com">Nik</a>' in html
        assert 'This is really great!' in html

    def test_notification_with_no_website(self):
        make_comment(name="Tom", email="tom@tom.com", notify=True).save()
        com = make_comment(name="Nik", email="nik@nik.com", body="This is really great!")
        send_watcher_emails(com, "This is really great!", {"title": "My Blog Post", "url": "http://blog.com/123"})
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.subject == f'[nedlive.net] A comment on "My Blog Post" from Nik'
        assert email.recipients() == ["tom@tom.com"]
        assert "\nhttp://blog.com/123\n" in email.body
        assert "\nname: Nik\n" in email.body
        assert "\nwebsite: ---" in email.body
        assert "\nThis is really great!\n" in email.body
        assert "To unsubscribe" in email.body

        assert len(email.alternatives) == 1
        assert email.alternatives[0][1] == "text/html"
        html = email.alternatives[0][0]
        assert '<p>A comment on <a href="http://blog.com/123">My Blog Post</a> by' in html
        assert 'Nik' in html
        assert 'This is really great!' in html

    def test_two_notifications(self):
        # Two comments mean two emails get sent.
        make_comment(name="Tom", email="tom@tom.com", notify=True).save()
        make_comment(name="Nik", email="nik@nik.com", notify=True).save()
        com = make_comment(name="Jo", email="jo@anne.com")
        send_args = dict(
            com=com,
            markdown_body="This is really great!",
            context={
                "title": "My Blog Post",
                "url": "http://blog.com/123",
            },
        )
        send_owner_email(**send_args)
        send_watcher_emails(**send_args)
        assert len(mail.outbox) == 3
        owner_email = mail.outbox[0]
        assert "\nnotifications to: nik@nik.com, tom@tom.com\n" in owner_email.body
        assert mail.outbox[1].subject == f'[nedlive.net] A comment on "My Blog Post" from Jo'
        assert mail.outbox[1].recipients() == ["nik@nik.com"]
        assert mail.outbox[2].subject == f'[nedlive.net] A comment on "My Blog Post" from Jo'
        assert mail.outbox[2].recipients() == ["tom@tom.com"]

    def test_no_duplicates(self):
        # Two comments from the same person, but they only get one email.
        make_comment(name="Tom", email="tom@tom.com", notify=True).save()
        make_comment(name="Nik", email="nik@nik.com", notify=True).save()
        make_comment(name="Nik", email="nik@nik.com", notify=True).save()
        com = make_comment(name="Jo", email="jo@anne.com")
        send_watcher_emails(com, "", {"title": "My Blog Post"})
        assert len(mail.outbox) == 2
        assert mail.outbox[0].subject == f'[nedlive.net] A comment on "My Blog Post" from Jo'
        assert mail.outbox[0].recipients() == ["nik@nik.com"]
        assert mail.outbox[1].subject == f'[nedlive.net] A comment on "My Blog Post" from Jo'
        assert mail.outbox[1].recipients() == ["tom@tom.com"]

    def test_notifications_only_from_the_same_post(self):
        # Notifications for one post don't get confused about other posts.
        make_comment(entryid="123", name="Tom", email="tom@tom.com", notify=True).save()
        make_comment(entryid="123", name="Nik", email="nik@nik.com", notify=True).save()
        make_comment(entryid="456", name="Sue", email="sue@sue.com", notify=True).save()
        com = make_comment(entryid="456", name="Jo", email="jo@anne.com")
        send_watcher_emails(com, "", {"title": "Another Blog Post"})
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == f'[nedlive.net] A comment on "Another Blog Post" from Jo'
        assert mail.outbox[0].recipients() == ["sue@sue.com"]
