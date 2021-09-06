import html
import re

def first_par(value):
    """ Take just the first paragraph of the HTML passed in.
    """
    return value.split("</p>")[0] + "</p>"


def inner_html(value):
    """ Strip off the outer tag of the HTML passed in.
    """
    if value.startswith('<'):
        value = value.split('>', 1)[1].rsplit('<', 1)[0]
    return value


def just_text(value):
    """ Remove non-text HTML tags (really just img for now).
    """
    # Remove all img tags
    noimg = re.sub(r"<img [^>]*>(</img>)?", "", value)
    # Now we might have empty <a> tags. Remove them..
    noemptya = re.sub(r"<a [^>]*></a>", "", noimg)
    return noemptya


def first_sentence(value, number=1):
    """ Take just the first `number` sentences of the HTML passed in.
    """
    number = int(number)
    assert number > 0
    value = inner_html(first_par(value))
    words = value.split()
    # Collect words until the result is a sentence.
    sentence = ""
    while words and number > 0:
        if sentence:
            sentence += " "
        sentence += words.pop(0)
        if not re.search(r'[.?!][)"]*$', sentence):
            # A sentence has to end with punctuation.
            continue
        if words and not re.search(r'^[("]*[A-Z0-9]', words[0]):
            # Next sentence has to start with upper case.
            continue
        if re.search(r'(Mr\.|Mrs\.|Ms\.|Dr\.| [A-Z]\.)$', sentence):
            # If the "sentence" ends with a title or initial, then it probably
            # isn't the end of the sentence.
            continue
        if sentence.count('(') != sentence.count(')'):
            # A sentence has to have balanced parens.
            continue
        if sentence.count('"') % 2:
            # A sentence has to have an even number of quotes.
            continue
        if sentence.count("&#8220;") != sentence.count("&#8221;"):
            # A sentence has to have as many open-double quotes as close.
            continue

        # We have a complete sentence.
        number -= 1

    return sentence


def description_safe(text):
    """Turn an HTML fragment into something that can be og:description."""
    # No html entities.
    text = html.unescape(text)
    # No text styling.
    text = re.sub(r"</?[bi]>", "", text)
    return text
