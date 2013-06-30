"""Help make graphviz diagrams."""

import cgi
import itertools
import os
import os.path
import subprocess

import cog
import Image


class Graphviz(object):
    SNIPS = {
        'INTATTRS':     'shape=circle',
        'NAMEATTRS':    'shape=box, style=filled, fillcolor=lightgray, fontname=monospace',
        'PROLOG':       'digraph d { graph [rankdir=LR, dpi=300]; node [fontsize=20, fontname=serif];',
        'EPILOG':       '}',
    }

    SCALE_FACTOR = 5

    def __init__(self):
        self.dot_lines = []
        self.names = set()
        self.default_alt = ""

    def dot(self, dot):
        self.dot_lines.append(dot)

    def as_dot(self):
        dot = "\n".join(self.dot_lines)
        dot = 'PROLOG {0} EPILOG'.format(dot)
        for short, long in self.SNIPS.iteritems():
            dot = dot.replace(short, long)
        return dot

    def codelabel(self, *lines):
        line_len = max(len(l) for l in lines)
        lines = [l.ljust(line_len) for l in lines]
        lines = "\n".join(lines).replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
        self.default_alt = lines
        lines += "\\n " # To add a blank line to space the label nicely
        self.dot('graph [label="{0}", labelloc="t", fontname="Courier Bold"];'.format(lines))

    def name(self, name):
        self.dot('{0} [NAMEATTRS]'.format(name))
        self.names.add(name)

    def int(self, i):
        self.dot('{0} [shape=circle]'.format(i))

    def refer(self, name, value):
        if name not in self.names:
            self.name(name)
        value = str(value)
        if value.startswith("list"):
            value = value+":0"
        self.dot('{0} -> {1}'.format(name, value))

    def list(self, sym, *elements):
        els = "|".join("<{0}>{1}".format(i, e) for i,e in enumerate(elements))
        self.dot('{0} [shape=record, label="{{{1}}}"]'.format(sym, els))

    def start_frame(self, label):
        self.dot('subgraph cluster_fn {')
        self.dot('  label="{0}"'.format(label))
        self.dot('  style="rounded, dashed"')

    def end_frame(self):
        self.dot('}')

    def make_png(self, dot_path):
        """Make a PNG file.

        Returns a tuple: ok, output

        """
        dot_dir = os.path.dirname(dot_path)
        if not os.path.exists(dot_dir):
            os.makedirs(dot_dir)

        dot_cmd = "dot -Tpng -o{0}".format(dot_path)
        p = subprocess.Popen(
            dot_cmd, shell=True,
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            stdout, stderr = p.communicate(self.as_dot())
        except (OSError, IOError) as e:
            stdout, stderr = p.stdout.read(), p.stderr.read()
            p.wait()

        ok = p.returncode == 0
        output = stdout + "\n" + stderr
        if not ok:
            return ok, output

        # Resize the image with PIL
        image = Image.open(dot_path)
        size = image.size
        new_size = (int(size[0]/self.SCALE_FACTOR), int(size[1]/self.SCALE_FACTOR))
        smaller = image.resize(new_size, Image.ANTIALIAS)
        smaller.save(dot_path)

        return ok, output


class CogGraphviz(Graphviz):
    # Where are we in the stellated tree
    HERE = 'text'
    DOT_DIR = 'names_dot'

    diagram_id = itertools.count()

    def img(self, alt=""):
        dot_file = 'd{0:03d}.png'.format(next(self.diagram_id))
        dot_path = os.path.join(self.DOT_DIR, dot_file)

        ok, output = self.make_png(dot_path)
        if not ok:
            raise Exception("dot couldn't process at line {0}:\n{1}".format(cog.firstLineNum, output))

        full_path = "/".join([self.HERE, self.DOT_DIR, dot_file])
        alt = alt or self.default_alt
        cog.outl('<img src="{0}" alt="{1}" align="top"/>'.format(full_path, cgi.escape(alt, quote=True)))
