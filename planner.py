#! /usr/bin/env python3

import sys

_, PLANFILE = sys.argv
# TODO: autodetect?
INDENT = 2
INDENTSTR = ' '*INDENT


def fail(lineno, *args):
    print("line {}:".format(lineno), *args, file=sys.stdout)
    sys.exit(-1)

def parseline(line):
    tokens = line.split(maxsplit=1)
    assert len(tokens) in [1,2]
    if len(tokens) == 1:
        left, rest = tokens[0], ""
    else:
        left, rest = line.split(maxsplit=1)

    if left.isdigit():
        return int(left), rest
    else:
        return None, line

def indentlevel(line):
    indents = 0
    while line.startswith(INDENTSTR):
        line = line[len(INDENTSTR):]
        indents += 1
    return indents

def process(lines):
    idx = [0]

    def peek():
        if idx[0] < len(lines):
            return lines[idx[0]]
        else:
            return None

    def pop():
        idx[0] += 1

    def buildtree(indent=0):
        tree = []
        while True:
            nxt = peek()
            lindent = indentlevel(nxt[1]) if nxt is not None else None
            if lindent is None or lindent < indent:
                return tree
            elif lindent >= indent:
                pop()
                tree.append( (nxt, buildtree(indent=indent+1)) )

    tree = buildtree()

    linesums = {}
    def digest(lineno, line, subtree):
        value, entry = parseline(line.lstrip())
        sm = 0
        for (clno, cln), ctree in subtree:
            bval = digest(clno, cln, ctree)
            sm += bval
        if len(subtree) > 0:
            if value is not None and sm != value:
                fail(lineno, "subtree sum does not match")
            value = sm
        assert lineno not in linesums
        if value is None:
            fail(lineno, "could not compute a subtree sum")
        linesums[(lineno,line)] = value
        return value

    for (lineno, line), subtree in tree:
        digest(lineno, line, subtree)

    for lineno,line in sorted(linesums.keys()):
        value, entry = parseline(line.lstrip())
        ilevel = indentlevel(line)
        iprefix = INDENTSTR*ilevel
        if value is None:
            print('{}{} {}'.format(iprefix, linesums[(lineno,line)], entry))
        else:
            print('{}{} {}'.format(iprefix, value, entry))

with open(PLANFILE) as f:
    lines = list(enumerate((l.strip('\n') for l in f), start=1))
    process(lines)
