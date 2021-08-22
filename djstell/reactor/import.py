import csv
import sys

import django
django.setup()

from djstell.reactor.models import Comment

with open(sys.argv[1]) as data:
    for i, d in enumerate(csv.DictReader(data), start=1):
        Comment(**d).save()
        if i % 100 == 0:
            print(".", end="", flush=True)
print(f"\n{i} rows imported")
