import pytest

from ..clean import convert_body


@pytest.mark.parametrize("html, cleaned", [
    ("<p>Hello</p>", "<p>Hello</p>"),
    ("Hello <script>alert('pwned')</script>", "<p>Hello alert(&#8217;pwned&#8217;)</p>"),
    ("go: ibm.com", '<p>go: <a href="http://ibm.com" rel="nofollow">ibm.com</a></p>'),
    ("look at foo.py", '<p>look at foo.py</p>'),
    ("go: [ibm](http://ibm.com)", '<p>go: <a href="http://ibm.com" rel="nofollow">ibm</a></p>'),
    ("go: <a class='x' href='http://ibm.com'>ibm</a>", '<p>go: <a href="&#8217;http://ibm.com&#8217;" rel="nofollow">ibm</a></p>'),
    ("<pre>ibm.com</pre>", "<pre>ibm.com</pre>"),
    ("My variable is called `_secret_`.", "<p>My variable is called <code>_secret_</code>.</p>"),
    ("My variable is called _secret_.", "<p>My variable is called _secret_.</p>"),
    ("""I said, "hello," didn't I?""", """<p>I said, &#8220;hello,&#8221; didn&#8217;t I?</p>"""),
    ("Line1\nLine2", "<p>Line1\nLine2</p>"),
    ("Line1\n\nLine2", "<p>Line1</p>\n\n<p>Line2</p>"),
    ("a [link](https://edx.org) to edx", '<p>a <a href="https://edx.org" rel="nofollow">link</a> to edx</p>'),
    ("code:\n\n```\nLine 1\nLine 2\n```\nMore commentary", "<p>code:</p>\n\n<pre><code>Line 1\nLine 2\n</code></pre>\n\n<p>More commentary</p>"),
    ("code:\n\n```python\nLine 1\nLine 2\n```\nMore commentary", "<p>code:</p>\n\n<pre><code>Line 1\nLine 2\n</code></pre>\n\n<p>More commentary</p>"),
])
def test_convert_body(html, cleaned):
    assert convert_body(html) == cleaned
