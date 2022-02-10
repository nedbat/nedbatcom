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
    h = html.unescape(h)
    h = h.partition("<script async")[0]
    h = h.strip()
    print(h)

if __name__ == "__main__":
    url = sys.argv[1]
    print(f"<!-- fetched and bx-tweaked by get-tweet.py from {url} -->")
    get_tweet(url)
