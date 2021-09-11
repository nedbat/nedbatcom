import csv
import sys

import ftfy

import django
django.setup()

from djstell.reactor.models import Comment

fix_config = ftfy.TextFixerConfig(uncurl_quotes=False)

def fix(v):
    if v == "NULL":
        return None
    else:
        return ftfy.fix_text(v, fix_config)

with open(sys.argv[1]) as data:
    for i, d in enumerate(csv.DictReader(data), start=1):
        fixed = {k: fix(v) for k, v in d.items()}

        if fixed["email"]:
            for before, after in [("(at)", "@"), ("(dot)", "."), ("[at]", "@"), ("[.]", ".")]:
                fixed["email"] = fixed["email"].replace(before, after)

        if fixed["body"]:
            fixed["body"] = fixed["body"].replace("\r\n", "\n").replace("\r", "\n")

        try:
            Comment(**fixed).save()
        except:
            print("Couldn't save row:")
            import pprint
            pprint.pprint(fixed)
            raise
        if i % 100 == 0:
            print(".", end="", flush=True)

print(f"\n{i} rows imported")
