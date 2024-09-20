"""
For making figures of Git histories.
"""

import cog
from cupid.svgfig import SvgFig

COMMITW = 45
COMMITGAP = 25
COMMITSTRIDE = COMMITW + COMMITGAP
MARGIN = 10
STROKE = 1.5

class Branch:
    def __init__(self, fig, x, y, pod=None):
        self.fig = fig
        self.curx = x
        self.cury = y
        self.head = pod

    def commit(self, name=None, **kwargs):
        circle_args = dict(
            center=(self.curx, self.cury),
            size=(COMMITW, COMMITW),
            stroke_width=STROKE,
            )
        circle_args.update(kwargs)
        if name:
            circle_args.update(text=name)
        c = self.fig.circle(**circle_args)
        if self.head:
            self.fig.connect(self.head.east, 0, c.west, 0)
        self.head = c
        self.curx += COMMITSTRIDE
        return c

    def merge(self, other, name, **kwargs):
        y = min(self.cury, other.cury)
        circle_args = dict(
            center=(self.curx, y),
            size=(COMMITW, COMMITW),
            stroke_width=STROKE
            )
        circle_args.update(kwargs)
        c = self.fig.circle(**circle_args, text=name)
        self.fig.connect(self.head.east, 0, c.west, 0)
        self.fig.connect(other.head.east, 0, c.south, 270)
        self.head = c
        self.curx += COMMITSTRIDE
        return c

class GitFig(SvgFig):
    def __init__(self, nbranches, ncommits, **kwargs):
        figw = (ncommits * COMMITW) + ((ncommits - 1) * COMMITGAP) + 2 * MARGIN
        figh = (nbranches * COMMITW) + ((nbranches - 1) * COMMITGAP) + 2 * MARGIN
        super().__init__(size=(figw, figh), **kwargs)
        self.curx = MARGIN + COMMITW / 2

    def branch(self, name, y, pod=None, advance=0):
        y = MARGIN + COMMITW / 2 + y * COMMITSTRIDE
        if pod is None:
            x = self.curx + COMMITSTRIDE * advance
        else:
            x = pod.cx + COMMITSTRIDE * advance
        return Branch(self, x, y, pod=pod)

    def finish(self):
        cog.outl(self.tostring())
