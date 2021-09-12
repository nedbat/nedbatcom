import pytest

from ..clean import convert_body


@pytest.mark.parametrize("html, cleaned", [
    ("<p>Hello</p>", "<p>Hello</p>"),
    ("Hello <script>alert('pwned')</script>", "<p>Hello alert('pwned')</p>"),
    ("go: ibm.com", '<p>go: <a href="http://ibm.com" rel="nofollow">ibm.com</a></p>'),
    ("look at foo.py", '<p>look at foo.py</p>'),
    ("go: <a href='http://ibm.com'>ibm</a>", '<p>go: <a href="http://ibm.com" rel="nofollow">ibm</a></p>'),
    ("go: <a class='x' href='http://ibm.com'>ibm</a>", '<p>go: <a href="http://ibm.com" rel="nofollow">ibm</a></p>'),
    ("<pre>ibm.com</pre>", "<pre>ibm.com</pre>"),
    ("My variable is called `_secret_`.", "<p>My variable is called <code>_secret_</code>.</p>"),
    ("Line1\nLine2", "<p>Line1\nLine2</p>"),
    ("Line1\n\nLine2", "<p>Line1</p>\n\n<p>Line2</p>"),
    ("a [link](https://edx.org) to edx", '<p>a <a href="https://edx.org" rel="nofollow">link</a> to edx</p>'),
])
def test_convert_body(html, cleaned):
    assert convert_body(html) == cleaned
