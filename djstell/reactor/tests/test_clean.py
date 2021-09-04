import pytest

from ..clean import clean_html


@pytest.mark.parametrize("html, cleaned", [
    ("<p>Hello</p>", "<p>Hello</p>"),
    ("Hello <script>alert('pwned')</script>", "Hello alert('pwned')"),
    ("go: ibm.com", 'go: <a href="http://ibm.com" rel="nofollow">ibm.com</a>'),
    ("look at foo.py", 'look at foo.py'),
    ("go: <a href='http://ibm.com'>ibm</a>", 'go: <a href="http://ibm.com" rel="nofollow">ibm</a>'),
    ("go: <a class='x' href='http://ibm.com'>ibm</a>", 'go: <a href="http://ibm.com" rel="nofollow">ibm</a>'),
    ("<pre>ibm.com</pre>", "<pre>ibm.com</pre>"),
])
def test_cleaning_html(html, cleaned):
    assert clean_html(html) == cleaned
