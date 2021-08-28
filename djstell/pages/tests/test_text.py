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
])
def test_just_text(text, result):
    assert just_text(text) == result

@pytest.mark.parametrize("text, result", [
    ("<b>tl;dr</b>: <i>Look!</i>", "tl;dr: Look!"),
    ("A&amp;B isn&#8217;t OK.", "A&B isn’t OK."),
])
def test_description_safe(text, result):
    assert description_safe(text) == result
