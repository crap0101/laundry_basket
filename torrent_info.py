#!/usr/bin/env python3

# Copyright (C) 2012-2025  Marco Chieppa (aka crap0101)

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


import argparse
from collections.abc import Mapping, MutableSequence
import sys

# external import
try:
    import bencode
except ImportError:
    import fastbencode as bencode

_VERSION = '0.4'

def print_info (seq, separator):
    for k, v in seq:
        if isinstance(v, bytes):
            v = v.decode('utf-8')
        print(k.decode('utf-8'), separator, v, sep='')

def get_data (file):
    with open(file, 'rb') as f:
        return bencode.bdecode(f.read())

def get_info (mapping, show_pieces=False):
    seq_info = []
    for k, v in mapping.items():
        if isinstance(v, Mapping):
            seq_info.extend(get_info(v))
        else:
            if not show_pieces and k == b'pieces':
                pass
            else:
                seq_info.append((k,v))
    return seq_info

def main(file, attrs=(),
         available=False, print_list=False, show_pieces=False,
         sep='', bare=False, ignore_err=False):
    attrs = tuple(bytes(a, 'utf-8') for a in attrs)
    info = get_info(get_data(file), show_pieces)
    if available:
        print_info([(k, '') for k,v in info], '')
    elif print_list:
        print_info(info, sep)
    else:
        info = dict(info)
        for attr in attrs:
            v = info.get(attr, None)
            if v is None:
                if not ignore_err:
                    raise KeyError(attr)
                else:
                    v = b'N.A.'
            if bare:
                attr = b''
                sep = ''
            print_info([(attr,v)], sep)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show torrent info.')
    parser.add_argument('files', nargs='+',
                        metavar='FILE', help='torrent files.')
    parser.add_argument('-b', '--bare',
                        dest='bare', action='store_true',
                        help='within -a, print only the value of the'
                        ' choosen attributes, in command-line order,'
                        ' one per line.')
    parser.add_argument('-i', '--ignore-attrs-err',
                        dest='ignore', action='store_true',
                        help='within -a, ignore errors for non-available'
                        ' choosen attributes')
    parser.add_argument('-p', '--show-pieces', action='store_true',
                        dest='pieces', help='show torrent pieces. Since this'
                        ' attribute is not human-readable by default'
                        ' is not displayed, use this option to see them')
    parser.add_argument('-s', '--separator',
                        dest='separator', default=' --> ',
                        help='string separator between'
                        ' key and value, default "%(default)s"')
    parser.add_argument('-v', '--version', action='version', version=_VERSION)
    mgroup = parser.add_mutually_exclusive_group(required=True)
    mgroup.add_argument('-a', '--attributes', dest='attrs', nargs='+',
                        default=(),
                        metavar='ATTR', help="Show only the choosen torrent's"
                        ' attributes.')
    mgroup.add_argument('-A', '--available',
                        dest='available', action='store_true',
                        help='Show, one per line, the available attributes.')

    mgroup.add_argument('-l', '--print-list',
                        dest='list', action='store_true',
                        help='list all key/value attribute pairs.')
    parsed = parser.parse_args()
    for file in parsed.files:
        main(file, parsed.attrs,
             parsed.available, parsed.list, parsed.pieces,
             parsed.separator, parsed.bare, parsed.ignore)

