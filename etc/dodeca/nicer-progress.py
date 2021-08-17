import os
import sys

width = os.get_terminal_size().columns
last = "Xyzzy"
for lineno, line in enumerate(sys.stdin, start=1):
    overwrite = (line.startswith("Fra:") and last.split() and line.split()[0] == last.split()[0])
    if overwrite:
        sys.stdout.write("\r")
    elif lineno > 1:
        sys.stdout.write("\n")
    sys.stdout.write(line.rstrip().ljust(width - 1))
    sys.stdout.flush()
    last = line
print()
