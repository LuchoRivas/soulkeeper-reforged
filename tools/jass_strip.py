#!/usr/bin/env python3
"""Removes /* ... */ block comments from a JASS file, keeping line numbers.

Usage:  python3 tools/jass_strip.py <in.j> <out.j>

The common.j and Blizzard.j in https://github.com/lep/jassdoc carry
/** ... */ documentation blocks, which pjass does not accept. This turns
them back into plain JASS so they can be used as pjass references.
Strings, rawcodes and // comments are left untouched.
"""
import sys


def strip(s):
    out = []
    i, n = 0, len(s)
    while i < n:
        if s.startswith('//', i):
            j = s.find('\n', i)
            j = n if j < 0 else j
            out.append(s[i:j])
            i = j
        elif s.startswith('/*', i):
            j = s.find('*/', i + 2)
            j = n if j < 0 else j + 2
            out.append('\n' * s.count('\n', i, j))
            i = j
        elif s[i] == '"':
            j = i + 1
            while j < n and s[j] != '"':
                j += 2 if s[j] == '\\' else 1
            out.append(s[i:j + 1])
            i = j + 1
        elif s[i] == "'":
            j = s.find("'", i + 1)
            j = n - 1 if j < 0 else j
            out.append(s[i:j + 1])
            i = j + 1
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    text = open(sys.argv[1], encoding='utf-8', errors='replace').read()
    open(sys.argv[2], 'w', encoding='utf-8', newline='\n').write(strip(text))
