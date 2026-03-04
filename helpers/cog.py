"""
Helpers for use with cog.
"""

from pathlib import Path

from edtext import EdText


def ed(filename):
    return EdText(Path(filename).read_text())


def code(text, lang=""):
    text = str(text)
    assert "]]" not in text, "Can't include ']]' in code text"
    if lang:
        langattr = f" lang='{lang}'"
    else:
        langattr = ""
    print(f"<code{langattr}><![CDATA[")
    print(text, end="")
    print("]]></code>")
