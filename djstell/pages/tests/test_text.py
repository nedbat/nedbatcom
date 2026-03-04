from textwrap import dedent

import pytest

from ..text import description_safe, first_sentence, just_text

@pytest.mark.parametrize("text, num, sentences", [
    ("<p>A dog. A cat.", 1, "A dog."),
    ("<p>A co-worker (hi Matt!) is having a baby. A cat.</p>", 1, "A co-worker (hi Matt!) is having a baby."),
    ('<p>A dog (canine!) said, "woof!" before. A cat.</p>', 1, 'A dog (canine!) said, "woof!" before.'),
    ('<p>A dog (canine!) said, "Woof! Woof!" before. A cat.</p>', 1, 'A dog (canine!) said, "Woof! Woof!" before.'),
    ("<p>Hello, Mr. Batchelder.</p>", 1, "Hello, Mr. Batchelder."),
    ("<p>A dog <i>barked</i> loudly.</p>", 1, "A dog <i>barked</i> loudly."),
])
def test_first_sentence(text, num, sentences):
    assert first_sentence(text, num) == sentences

@pytest.mark.parametrize("text, result", [
    ("<p><a href='foo'><img src='bar'></a>My son Max</p>", "<p>My son Max</p>"),
    ("<p><a href='foo'>My son</a> Max</p>", "<p>My son Max</p>"),
    (
        dedent("""\
            <a href='http://twopoint718.blogspot.com/2009/03/march-5-is-square-root-of-christmas.html'>Chris Wilson</a>
            notices a mathematical-calendrical quirk: if March 5th is 35,
            then 35<span class="times">×</span>35 = 1225 means that March 5th squared is December 25th, so
            March 5th is the square root of Christmas!  Pair this with Pi Day (3/14), and
            <a href='http://twopoint718.blogspot.com/2009/03/march-5-is-square-root-of-christmas.html'>you get a nerd celebration</a>:
        """),
        dedent("""\
            Chris Wilson
            notices a mathematical-calendrical quirk: if March 5th is 35,
            then 35×35 = 1225 means that March 5th squared is December 25th, so
            March 5th is the square root of Christmas!  Pair this with Pi Day (3/14), and
            you get a nerd celebration:
        """),
    ),
])
def test_just_text(text, result):
    assert just_text(text) == result

@pytest.mark.parametrize("text, result", [
    ("<b>tl;dr</b>: <i>Look!</i>", "tl;dr: Look!"),
    ("A&amp;B isn&#8217;t OK.", "A&B isn’t OK."),
])
def test_description_safe(text, result):
    assert description_safe(text) == result
