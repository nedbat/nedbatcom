"""
Helpers for use with cog.
"""

from pathlib import Path

from edtext import EdText


def include_section(filename, start, end, prelude="", postlude=""):
    """
    Grab a part of a file, and print it for inclusion with cog.

    Args:
        start (str): The text marking the start of the section. This line is not
            included in the output.
        end (str): The text marking the end of the section. This line is not
            included in the output.
        prelude (str): Line(s) to be output before the section.
        postlude (str): Line(s) to be output after the section.

    """
    with open(filename) as f:
        lines = list(f)
    start_num = next(line_num for line_num, line in enumerate(lines) if line.strip() == start)
    end_num = next(line_num for line_num, line in enumerate(lines[start_num:], start=start_num) if line.strip() == end)
    if prelude:
        print(prelude)
    print("".join(lines[start_num+1: end_num]), end="")
    if postlude:
        print(postlude)


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
