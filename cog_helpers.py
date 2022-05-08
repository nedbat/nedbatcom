"""
Run with a tweet url argument, it will output XML to go into a .bx file.

https://developer.twitter.com/en/docs/twitter-for-websites/embedded-tweets/overview

"""

import html
import json
import sys

import requests

def get_tweet(url):
    oembed = requests.get(f"https://publish.twitter.com/oembed?url={url}").json()
    h = oembed["html"]
    h = h.replace("<br>", "<br/>")
    # Seems like there ought to be a better way to convert &mdash; to —, but
    # also keep &amp; as-is. Oh well.
    h = h.replace("&amp;", "@@@@AMP@@@@")
    h = html.unescape(h)
    h = h.replace("@@@@AMP@@@@", "&amp;")
    h = h.partition("<script async")[0]
    h = h.strip()
    print(h)

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

if __name__ == "__main__":
    url = sys.argv[1]
    print(f"<!-- fetched and bx-tweaked by get-tweet.py from {url} -->")
    get_tweet(url)
