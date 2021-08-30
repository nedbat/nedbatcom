import dataclasses
import re
import time

import lxml.html
import pytest

from ..models import Comment


def has_error(response, msg):
    assert f"<p class='errormsg'>{msg}</p>".encode("utf8") in response.content

def errors(response):
    dom = lxml.html.fromstring(response.content)
    error_msgs = dom.cssselect("p.errormsg")
    return [msg.text for msg in error_msgs]

def content(response):
    content = re.sub(r"\s+", " ", response.content.decode("utf8"))
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
    dom = lxml.html.fromstring(response.content)
    inputs = dom.cssselect("#commentformform input, #commentformform textarea")
    return Inputs(inputs)

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


@pytest.mark.django_db(databases=['default', 'reactor'])
class TestSaving:
    def test_comment(self, client):
        response = client.get(BLOG_POST)
        assert "<span class='react'>&#xbb;&#xa0; react </span>" in content(response)
        assert Comment.objects.filter(entryid=ENTRYID).count() == 0
        inputs = input_fields(response)
        inputs["name"] = "Thomas Edison"
        inputs["email"] = "tom@edison.org"
        inputs["body"] = "This is a great blog post"
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        inputs = input_fields(response)
        response = client.post(BLOG_POST, inputs.post_data("addbtn"))
        assert "Thomas Edison" in content(response)
        assert "tom@edison.org" in content(response)
        assert "This is a great blog post" in content(response)

        response = client.get(BLOG_POST)
        assert "<span class='react'>&#xbb;&#xa0; 1 reaction </span>" in content(response)
        assert "Thomas Edison" in content(response)
        assert "tom@edison.org" in content(response)
        assert "This is a great blog post" in content(response)
        assert errors(response) == []
        assert Comment.objects.filter(entryid=ENTRYID).count() == 1

        inputs["name"] = "Nikola Tesla"
        inputs["email"] = "nik@tesla.com"
        inputs["body"] = "I agree"
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        dom = lxml.html.fromstring(response.content)
        previews = dom.cssselect(".comment.preview")
        assert len(previews) == 1
        assert "Thomas Edison" in content(response)
        assert "tom@edison.org" not in content(response)
        assert "This is a great blog post" in content(response)
        assert "Nikola Tesla" in content(response)
        assert "nik@tesla.com" in content(response)
        assert "I agree" in content(response)
        inputs = input_fields(response)

        response = client.post(BLOG_POST, inputs.post_data("addbtn"))
        assert errors(response) == []
        assert Comment.objects.filter(entryid=ENTRYID).count() == 2
        assert "Thomas Edison" in content(response)
        assert "tom@edison.org" not in content(response)
        assert "This is a great blog post" in content(response)
        assert "Nikola Tesla" in content(response)
        assert "nik@tesla.com" in content(response)
        assert "I agree" in content(response)

        response = client.get(BLOG_POST)
        assert "<span class='react'>&#xbb;&#xa0; 2 reactions </span>" in content(response)
        assert "Thomas Edison" in content(response)
        assert "tom@edison.org" not in content(response)
        assert "This is a great blog post" in content(response)
        assert "Nikola Tesla" in content(response)
        assert "nik@tesla.com" in content(response)
        assert "I agree" in content(response)
