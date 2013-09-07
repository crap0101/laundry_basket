#!/usr/bin/env python

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
import argparse
from collections import Mapping
import platform
import sys
if platform.python_version_tuple()[0] < '3':
    input = raw_input

# external import
import bencode

_VERSION = '0.3'

def main(file, attrs=(), interactive=False, show_pieces=False):
    with open(file, 'rb') as file:
        meta = bencode.bdecode(file.read())
    if attrs:
        for attr in attrs:
            print(attr, meta[attr], sep=': ')
        return
    for key in meta:
        info = meta[key]
        while True:
            try:
                if interactive:
                    if isinstance(info, Mapping):
                        print(key, list(info.keys()))
                        choice = input("choice: ").encode('utf-8')
                        print(info.get(choice,
                                       "{0}: invalid key".format(choice)))
                    else:
                        print(key, meta[key], sep=': ')
                        break
                else:
                    if isinstance(info, Mapping):
                        if not show_pieces:
                            info.pop('pieces', "No key named 'pieces'")
                        for k, v in info.items():
                            print(k, v, sep=': ')
                    else:
                        print(key, meta[key], sep=': ')
                    break
            except KeyboardInterrupt as e:
                print()
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show torrent info.')
    parser.add_argument('torrent_file', metavar='FILE', help='torrent file.')
    parser.add_argument('-a', '--attributes', dest='attrs', nargs='+',
                        metavar='ATTR', help="Show only this torrent's"
                        ' attributes and exit. With this option, the presence'
                        ' of the -i/--interactive option is ignored.')
    parser.add_argument('-i', '--interactive', action='store_true',
                        dest='i', help='interactive mode, browse torrent'
                        ' attributes, if available.')
    parser.add_argument('-p', '--show-pieces', action='store_true',
                        dest='p', help='show torrent pieces. Since this'
                        ' attribute is not human-readable by default'
                        ' is not displayed, use this option to see them.')
    parser.add_argument('-v', '--version', action='version', version=_VERSION)
    parsed = parser.parse_args()
    main(parsed.torrent_file, parsed.attrs, parsed.i, parsed.p)
