import dataclasses
import re
import time

import lxml.html
import pytest

def has_error(response, msg):
    assert f"<p class='errormsg'>{msg}</p>".encode("utf8") in response.content

BLOG_POST = "/blog/200203/my_first_job_ever.html"

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
        assert inputs["entryid"] == "e20020307T000000"
        assert inputs["previewbtn"] == "Preview >>"
        assert inputs["honeybtn"] == "I'm a spambot"

    def test_no_data(self, client):
        response = client.post(BLOG_POST, {})
        has_error(response, "Something is wrong with the timestamp")

    def test_future_timestamp(self, client):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        inputs["timestamp"] = str(int(inputs["timestamp"]) + 30)
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        has_error(response, "A post from the future!")

    def test_old_timestamp(self, client):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        inputs["timestamp"] = str(int(inputs["timestamp"]) - 35*60)
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        has_error(response, "You took a long time entering this post. Please preview it and submit it again.")

    @pytest.mark.parametrize("hnum", "1234")
    def test_honeypot_fields(self, client, hnum):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        inputs[f"honey{hnum}"] = "x"
        response = client.post(BLOG_POST, inputs.post_data("previewbtn"))
        has_error(response, "Go away stupid bear")

    def test_honeypot_button(self, client):
        response = client.get(BLOG_POST)
        inputs = input_fields(response)
        response = client.post(BLOG_POST, inputs.post_data("honeybtn"))
        has_error(response, "Go away stupid bear")
