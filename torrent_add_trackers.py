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

import os
import sys
import argparse

import bencode

_VERSION = '0.1'

ANNOUNCE = 'announce'
ANNOUNCE_LIST = 'announce-list'


def flatlist (lst):
    res = []
    for e in lst:
        if isinstance(e, list):
            res.extend(flatlist(e))
        else:
            res.append(e)
    return res

def add_trackers (path, trackers, backup_suffix='.bk'):
    with open(path, 'rb') as file:
        data = file.read()
    meta = bencode.bdecode(data)
    alist = meta.get(ANNOUNCE_LIST, [meta[ANNOUNCE]])
    trackerlist = flatlist(alist)
    alist.extend([t] for t in set(trackers).difference(trackerlist))
    meta[ANNOUNCE_LIST] = alist
    if backup_suffix:
        os.rename(path, path+backup_suffix)
    with open(path, 'wb') as file:
        file.write(bencode.bencode(meta))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('file', help='torrent file')
    p.add_argument('trackers', nargs='+', help='trakers to add')
    p.add_argument('-b', '--backup', dest='backup', nargs='?', const='.bk',
                   default='', metavar='SUFFIX', help='make a backup of the'
                   ' original file, renamed adding SUFFIX. Default: %(const)s')
    p.add_argument('-f', '--from-file', dest='from_file', metavar='PATH',
                   help='read trackers for PATH (one per line).')
    p.add_argument('-v', '--version', action='version', version=_VERSION)
    args = p.parse_args()
    if args.from_file:
        with open(args.from_file) as tfile:
            args.trackers.extend(t.strip() for t in tfile)
    add_trackers(args.file, args.trackers, args.backup)
