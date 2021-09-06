import dataclasses
import datetime
import re
import time

import lxml.html
import pytest

from django.core import mail

from ..models import Comment
from .. import honey

def has_error(response, msg):
    assert f"<p class='errormsg'>{msg}</p>".encode("utf8") in response.content

def errors(response):
    error_msgs = cssselect(response, "p.errormsg")
    return [msg.text for msg in error_msgs]

def inner_html(node):
    from lxml.etree import tostring
    from itertools import chain
    parts = ([node.text] +
            list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) +
            [node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts)).strip()

def text_content(node):
    return node.text_content().strip()

def comments(response):
    comments = []
    for comdiv in cssselect(response, "div.comment.published"):
        comments.append({
            "name": text_content(comdiv.cssselect(".who")[0]),
            "when": squish_white(text_content(comdiv.cssselect(".when")[0])),
            "body": inner_html(comdiv.cssselect(".commenttext")[0]),
        })
    return comments

def squish_white(text):
    text = re.sub(r"\s+", " ", text)
    return text

def content(response):
    content = squish_white(response.content.decode("utf8"))
    return content

def save(response):
    with open("bad.html", "wb") as f:
        f.write(response.content)

BLOG_POST = "/blog/200203/my_first_job_ever.html"
ENTRYID = "e20020307T000000"

# This is the order of field names in comments.html
FIELD_NAMES = """\
    name
    honey1 email honey2
    website
    honey3 body honey4
    notify previewbtn honeybtn
    entryid spinner timestamp
    addbtn
""".split()

@dataclasses.dataclass
class Input:
    name: str
    value: str
    type: str

    @classmethod
    def from_input(cls, inp):
        return cls(
            inp.name,
            inp.value or "",
            getattr(inp, "type", "textarea"),
        )

class Inputs:
    def __init__(self, inputs):
        self.inputs = dict(zip(FIELD_NAMES, map(Input.from_input, inputs)))

    def __getitem__(self, name):
        return self.inputs[name].value

    def __setitem__(self, name, value):
        self.inputs[name].value = value

    def post_data(self, btnname):
        assert btnname in self.inputs
        data = {
            inp.name: inp.value
            for label, inp in self.inputs.items()
            if label == btnname or inp.type != "submit"
        }
        return data

def input_fields(response):
    inputs = cssselect(response, "#commentformform input, #commentformform textarea")
    return Inputs(inputs)

def cssselect(response, selector):
    dom = lxml.html.fromstring(response.content)
    return dom.cssselect(selector)

@pytest.mark.django_db(databases=['default', 'reactor'])
class TestPosting:
    def test_get(self, client):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        # Check that we got the fields right
        assert re.fullmatch(r"[0-9a-f]{32}", inputs["spinner"])
        t = int(inputs["timestamp"])
        now = time.time()
        assert (now - 5) < t < (now + 5)
        assert inputs["entryid"] == ENTRYID
        assert inputs["previewbtn"] == "Preview >>"
        assert inputs["honeybtn"] == "I'm a spambot"

    def test_no_data(self, client):
        response = client.post(BLOG_POST, {})
        assert "Something is wrong with the timestamp" in errors(response)

    def test_future_timestamp(self, client):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        inputs["timestamp"] = str(int(inputs["timestamp"]) + 30)
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        assert "A post from the future!" in errors(response)

    def test_old_timestamp(self, client):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        inputs["timestamp"] = str(int(inputs["timestamp"]) - 35*60)
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        assert "You took a long time entering this post. Please preview it and submit it again." in errors(response)

    @pytest.mark.parametrize("hnum", "1234")
    def test_honeypot_fields(self, client, hnum):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        inputs[f"honey{hnum}"] = "x"
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        assert "Go away stupid bear" in errors(response)

    def test_honeypot_button(self, client):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        response = client.post(BLOG_POST, inputs.post_data("honeybtn"))
        assert "Go away stupid bear" in errors(response)

    def test_notify_but_no_email(self, client):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        inputs["name"] = "Joe No Email"
        inputs["website"] = "https://noemail.com"
        inputs["notify"] = "on"
        inputs["body"] = "Please send me future comments!"
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        assert "You can't get future comments if you don't provide an email." in errors(response)


@pytest.mark.django_db(databases=['default', 'reactor'])
class TestSaving:
    @pytest.mark.freeze_time
    def test_commenting(self, client, freezer):
        freezer.move_to('2020-09-01 07:34')
        # Tom reads.
        response = client.get(BLOG_POST)
        assert "<span class='react'>&#xbb;&#xa0; react </span>" in content(response)
        assert Comment.objects.filter(entryid=ENTRYID).count() == 0

        # Tom writes.
        inputs = input_fields(response)
        inputs["name"] = "Thomas Edison"
        inputs["email"] = "tom@edison.org"
        inputs["body"] = "This is a great blog post"

        # Tom previews.
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        inputs = input_fields(response)
        assert inputs["name"] == "Thomas Edison"
        assert inputs["email"] == "tom@edison.org"
        assert inputs["body"] == "This is a great blog post"

        # Tom adds.
        response = client.post(BLOG_POST, inputs.post_data("addbtn"))
        assert "Thomas Edison" in content(response)
        assert "tom@edison.org" in content(response)
        assert "This is a great blog post" in content(response)

        # What email got sent?
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.subject == "Someone commented"
        assert email.recipients() == ["ned@nedbatchelder.com"]
        assert email.from_email == "reactor@nedbatchelder.com"
        assert email.body == "THE BODY"

        # What does the world look like now?
        response = client.get(BLOG_POST)
        assert "<span class='react'>&#xbb;&#xa0; 1 reaction </span>" in content(response)
        assert comments(response) == [
            {'body': 'This is a great blog post', 'name': 'Thomas Edison', 'when': '7:34 AM on 1 Sep 2020'},
            ]
        assert errors(response) == []
        assert Comment.objects.filter(entryid=ENTRYID).count() == 1
        comment = Comment.objects.filter(entryid=ENTRYID)[0]
        assert comment.name == "Thomas Edison"
        assert comment.email == "tom@edison.org"
        assert comment.body == "This is a great blog post"
        assert comment.posted == datetime.datetime(2020, 9, 1, 7, 34, 0)
        assert comment.notify is False
        inputs = input_fields(response)
        assert inputs["name"] == "Thomas Edison"
        assert inputs["email"] == "tom@edison.org"
        assert inputs["body"] == ""

        mail.outbox = []
        freezer.move_to('2021-06-16 17:34')
        # Nikola reads.
        response = client.get(BLOG_POST)

        # Nikola writes.
        inputs = input_fields(response)
        inputs["name"] = "Nikola Tesla"
        inputs["email"] = "nik@tesla.com"
        inputs["body"] = "I agree"
        inputs["notify"] = "on"

        # Nikola previews.
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        inputs = input_fields(response)
        assert errors(response) == []
        previews = cssselect(response, ".comment.preview")
        assert len(previews) == 1
        assert comments(response) == [
            {'body': 'This is a great blog post', 'name': 'Thomas Edison', 'when': '7:34 AM on 1 Sep 2020'},
            ]
        assert "Nikola Tesla" in content(response)
        assert "nik@tesla.com" in content(response)
        assert "I agree" in content(response)

        # Nikola adds.
        response = client.post(BLOG_POST, inputs.post_data("addbtn"))
        assert errors(response) == []
        assert comments(response) == [
            {'body': 'This is a great blog post', 'name': 'Thomas Edison', 'when': '7:34 AM on 1 Sep 2020'},
            {'body': 'I agree', 'name': 'Nikola Tesla', 'when': '5:34 PM on 16 Jun 2021'},
            ]
        assert Comment.objects.filter(entryid=ENTRYID).count() == 2
        comment = Comment.objects.filter(entryid=ENTRYID).order_by("posted")[1]
        assert comment.name == "Nikola Tesla"
        assert comment.email == "nik@tesla.com"
        assert comment.body == "I agree"
        assert comment.posted == datetime.datetime(2021, 6, 16, 17, 34, 0)
        assert comment.notify is True

        # What does the world look like now?
        response = client.get(BLOG_POST)
        assert "<span class='react'>&#xbb;&#xa0; 2 reactions </span>" in content(response)
        assert comments(response) == [
            {'body': 'This is a great blog post', 'name': 'Thomas Edison', 'when': '7:34 AM on 1 Sep 2020'},
            {'body': 'I agree', 'name': 'Nikola Tesla', 'when': '5:34 PM on 16 Jun 2021'},
            ]
        assert len(mail.outbox) == 1

        mail.outbox = []
        freezer.move_to('2021-10-18 11:22')
        # Tom writes again.
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        inputs["name"] = "Thomas Edison"
        inputs["email"] = "tom@edison.org"
        inputs["body"] = "Thank you"

        # Tom previews.
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        inputs = input_fields(response)

        # Tom adds.
        response = client.post(BLOG_POST, inputs.post_data("addbtn"))

        # What email got sent?
        assert len(mail.outbox) == 2
        email = mail.outbox[0]
        assert email.subject == "Someone commented"
        assert email.recipients() == ["ned@nedbatchelder.com"]
        assert email.from_email == "reactor@nedbatchelder.com"
        assert email.body == "THE BODY"

        email = mail.outbox[1]
        assert email.subject == "A comment on BLAH"
        assert email.recipients() == ["nik@tesla.com"]
        assert email.from_email == "reactor@nedbatchelder.com"
        assert email.body == "HERE IS THE BODY"

    @pytest.mark.freeze_time
    def test_bleaching(self, client, freezer, monkeypatch):
        freezer.move_to('2020-10-18 01:23')
        # Check that clean_html is used on the body of the comment.
        def fake_clean_html(html):
            assert html == "<p>Hello</p>"
            return "CLEANED"
        monkeypatch.setattr(honey, "clean_html", fake_clean_html)

        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        inputs["name"] = "Bad Guy"
        inputs["email"] = "bad@guy.org"
        inputs["body"] = "<p>Hello</p>"
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        assert "CLEANED" in content(response)
        inputs = input_fields(response)
        inputs["body"] = "<p>Hello</p>"
        response = client.post(BLOG_POST, inputs.post_data("addbtn"))
        assert "CLEANED" in content(response)

        response = client.get(BLOG_POST)
        assert comments(response) == [
            {'body': 'CLEANED', 'name': 'Bad Guy', 'when': '1:23 AM on 18 Oct 2020'},
        ]
        comment = Comment.objects.filter(entryid=ENTRYID)[0]
        assert comment.body == "CLEANED"

    def test_block_too_many_links(self, client):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        inputs["name"] = "Bad Guy"
        inputs["email"] = "bad@guy.org"
        inputs["body"] = "ibm.com foo.com bar.com baz.com quux.com"
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        assert errors(response) == ["Too many links is suspicious"]
