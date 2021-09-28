"""Validators for comment data."""

import re


def valid_email(email):
    return (
        bool(re.fullmatch(r"[^@ ]+@[^@ ]+\.[^@ ]+", email)) and
        not email.startswith("mailto:")
    )

def valid_name(name):
    return (
        name.count("\n") == 0 and
        len(name) < 50 and
        not valid_email(name) and
        not valid_website(name) and
        re.search(r"[a-zA-Z]", name)
    )

def valid_website(website):
    return bool(re.fullmatch(r"https?://[-\w]+\.[-\w]+.*", website))
