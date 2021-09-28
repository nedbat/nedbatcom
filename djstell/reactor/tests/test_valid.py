import pytest

from ..valid import valid_email, valid_name, valid_website

@pytest.mark.parametrize("email", [
    "ned@edx.org",
    "hey123@foo.bar.baz",
])
def test_good_emails(email):
    assert valid_email(email)

@pytest.mark.parametrize("email", [
    "ned.edx.org",
    "hey123_foo.bar.baz",
    "hello",
    "https://foo.bar",
    "ned@edx",
    "ned@@edx.org",
    "mailto:ned@edx.org",
])
def test_bad_emails(email):
    assert not valid_email(email)

@pytest.mark.parametrize("website", [
    "http://foo.com",
    "http://geocities.com/~ned/homepage.htm",
    "https://foo.123.bar.com",
    "https://123.bar.com",
    "https://thomas-guettler.de",
])
def test_good_websites(website):
    assert valid_website(website)

@pytest.mark.parametrize("website", [
    "ned.edx.org",
    "ned@edx.org",
    "mailto:ned@edx.org",
    "nedbat.com/blog/index.html",
    "http://geocities/~ned/homepage.htm",
])
def test_bad_website(website):
    assert not valid_website(website)

@pytest.mark.parametrize("name", [
    "Ned",
    "Ned Batchelder",
    "Thomas Q. Edison",
    "john o'hearn"
])
def test_good_names(name):
    assert valid_name(name)

@pytest.mark.parametrize("name", [
    "lorem ipsum quia dolor sit amet consectetur adipisci velit",
    "ned@edx.org",
])
def test_bad_name(name):
    assert not valid_name(name)
