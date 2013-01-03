"""
Usage: grep [OPTION]... PATTERN [FILE] ...
Search for PATTERN in each FILE or standard input.
Example: grep -i 'hello world' menu.h main.c

Regexp selection and interpretation:
  -E, --extended-regexp     PATTERN is an extended regular expression
  -F, --fixed-strings       PATTERN is a set of newline-separated strings
  -G, --basic-regexp        PATTERN is a basic regular expression
  -e, --regexp=PATTERN      use PATTERN as a regular expression
  -f, --file=FILE           obtain PATTERN from FILE
  -w, --word-regexp         force PATTERN to match only whole words
  -x, --line-regexp         force PATTERN to match only whole lines
  -z, --null-data           a data line ends in 0 byte, not newline

Miscellaneous:
  -s, --no-messages         suppress error messages
  -v, --invert-match        select non-matching lines
      --mmap                use memory-mapped input if possible

Output control:
  -b, --byte-offset         print the byte offset with output lines
  -H, --with-filename       print the filename for each match
  -h, --no-filename         suppress the prefixing filename on output
  -q, --quiet, --silent     suppress all normal output
      --binary-files=TYPE   assume that binary files are TYPE
                            TYPE is 'binary', 'text', or 'without-match'.
  -a, --text                equivalent to --binary-files=text
  -I                        equivalent to --binary-files=without-match
  -d, --directories=ACTION  how to handle directories
                            ACTION is 'read', 'recurse', or 'skip'.
  -r, --recursive           equivalent to --directories=recurse.
  -L, --files-without-match only print FILE names containing no match
  -l, --files-with-matches  only print FILE names containing matches
  -c, --count               only print a count of matching lines per FILE
  -Z, --null                print 0 byte after FILE name

Context control:
  -NUM                      same as --context=NUM
  -U, --binary              do not strip CR characters at EOL (MSDOS)
  -u, --unix-byte-offsets   report offsets as if CRs were not there (MSDOS)

`egrep' means `grep -E'.  `fgrep' means `grep -F'.
With no FILE, or when FILE is -, read standard input.  If less than
two FILEs given, assume -h.  Exit status is 0 if match, 1 if no match,
and 2 if trouble.

Report bugs to <bug-gnu-utils@gnu.org>."""

import sys, re, getopt

class Queue:
	def __init__(self, size):
		self.size = size
		self.values = []

	def append(self, value):
		if self.size:
			self.values.append(value)
			while len(self.values) > self.size:
				self.values.pop(0)

	def pop(self):
		if self.values:
			return self.values.pop(0)
		return None

	def __len__(self):
		return len(self.values)

	def __getitem__(self, n):
		return self.values[n]


def grep(pattern, f, options):
	if options.whole_word:
		pattern = r"\b" + pattern + r"\b"
	if options.ignore_case:
		p = re.compile(pattern, re.I)
	else:
		p = re.compile(pattern)

	queue = Queue(options.before_context)
	line_nb = 0
	from_line = -1
	to_line = -1
	last_line = 0 # Last printed line.
	total = 0

	while 1:
		l = f.readline()
		line_nb += 1
		if not l:
			break

		match = 0
		if re.search(p, l):
			from_line = line_nb - options.before_context
			to_line = line_nb + options.after_context
			match = 1
			total += 1

		if line_nb <= to_line:
			if options.before_context or options.after_context:
				if last_line and from_line > last_line + 1:
					sys.stdout.write("--\n")

			from_line = max(from_line, last_line + 1, -len(queue))
			for i in range(from_line - line_nb, 0):
				if options.line_number:
					sys.stdout.write("%d-" % (i + line_nb))
				sys.stdout.write(queue[i])

			if options.line_number:
				if match:
					sys.stdout.write("%d:" % line_nb)
				else:
					sys.stdout.write("%d-" % line_nb)
			elif options.file_and_line:
				sys.stdout.write("%s(%d): " % (f.name, line_nb))
			sys.stdout.write(l)
			last_line = line_nb
		queue.append(l)

	return total

def printUsage():
	"""Print the help string that should printed by grep.py -h"""
	print "usage: grep.py [options] pattern [file]"
	print """
  -i, --ignore-case         ignore case distinctions
  -B, --before-context=NUM  print NUM lines of leading context
  -A, --after-context=NUM   print NUM lines of trailing context
  -C, --context[=NUM]       print NUM (default 2) lines of output context
                            unless overridden by -A or -B
  -n, --line-number         print line number with output lines
  -V, --version             print version information and exit
  -w, --word-regexp         force PATTERN to match only whole words
      --help                display this help and exit

See http://www.vdesmedt.com/~vds2212/grep.html for informations and updates.
Send an email to vivian@vdesmedt.com for comments and bug reports."""


def printVersion():
	print "pygrep.py version 0.6.0"


class Options:
	def __init__(self):
		self.ignore_case = 0
		self.before_context = 0
		self.after_context = 0
		self.line_number = 0
		self.file_and_line = 0
		self.whole_word = 0

def main(argv):
	options = Options()

	opts, args = getopt.getopt(argv, "ViA:B:C:nw", ["help", "version", "ignore-case", "before-context=", "after-context=", "context=", "line-number", "word-regexp"])
	for o, v in opts:
		if o in ["-i", "--ignore-case"]:
			options.ignore_case = 1
		if o in ["-A", "--after-context"]:
			options.after_context = int(v)
		if o in ["-B", "--before-context"]:
			options.before_context = int(v)
		if o in ["-C", "--context"]:
			if not v:
				v = 2
			options.after_context = int(v)
			options.before_context = int(v)
		if o in ["-n", "--line-number"]:
			options.line_number = 1
		if o in ["-w", "--word-regexp"]:
			options.whole_word = 1
		elif o in ["-V", "--version"]:
			printVersion()
			return 0
		elif o in ["--help"]:
			printUsage()
			return 0

	if len(args) <= 0:
		printUsage()
		return 1

	pattern = args[0]

	if len(args) == 1:
		return grep(pattern, sys.stdin, options)
	if args[1][0] == '@':
		options.file_and_line = 1
		total = 0
		ffile = open(args[1][1:])
		for fname in ffile.readlines():
			f = None
			try:
				f = open(fname.strip())
			except:
				pass
			if f:
				total += grep(pattern, f, options)
		sys.stdout.write("total found: %d\n\n\n" % total)
	else:
		f = open(args[1])
	return grep(pattern, f, options)
	f.close()


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
	