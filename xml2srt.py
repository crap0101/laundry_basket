#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2012  Marco Chieppa (aka crap0101)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import print_function

import io
import sys
import argparse
from xml.etree.ElementTree import ElementTree
from xml.sax.saxutils import unescape

_VERSION = '0.1'
DESCRIPTION = """
Convert xml subtitles to subrip (*.srt) format.
NOTE: used for TTML on youtube loooong time ago.
Needs some upgrade for works in other contexts.
https://www.w3.org/TR/ttml1/
"""

TRANSCRIPT = 'transcript'
TEXT = 'text'
START_TIME = 'start'
DURATION = 'dur'

ENCODING = 'utf-8'
ESCAPES = {'&amp;#39;': "'",
           '&#39;': "'",
           '&amp;quot;': '"',
           '&quot;': '"',
           }


def format_time_srt (seconds):
    h = seconds / 3600
    m, s  = divmod(seconds, 60)
    ms = (s - int(s))*1000
    return "{:02d}:{:02d}:{:02d},{:03d}".format(*map(int, (h,m,s,ms)))


def get_tree (path):
    tree = ElementTree()
    tree.parse(path)
    return tree


def srt_blocks (tree, text=TEXT, s=START_TIME, d=DURATION,
             escapes=ESCAPES, encoding=ENCODING):
    for n, item in enumerate(tree.iterfind(text), start=1):
        start, dur = map(float, (item.get(s), item.get(d)))
        yield "{num}\n{} --> {}\n{text}\n\n".format(
            num=n,
            text=unescape(item.text.strip(), escapes).encode(encoding),
            *map(format_time_srt, (start,start+dur)))


def get_args (args=None):
    p = argparse.ArgumentParser(description=DESCRIPTION)
    p.add_argument('-e', '--encoding', dest='enc', default=ENCODING,
                   help='file encoding. Default: %(default)s')
    p.add_argument('-i', '--input-file', dest='infile', default=sys.stdin,
                   help='input file (default: stdin)')
    p.add_argument('-o', '--output-file', dest='outfile', default=sys.stdout,
                   help='output file (default: stdout)')
    p.add_argument('-v', '--version', action='version', version=_VERSION)
    return p.parse_args(args)


if __name__ == '__main__':
    args = get_args()
    if args.outfile != sys.stdout:
        args.outfile = io.open(args.outfile, 'w', encoding=args.enc)
    for block in srt_blocks(get_tree(args.infile), encoding=args.enc):
        args.outfile.write(block.decode(args.enc))
    if args.outfile != sys.stdout:
        args.outfile.close()
