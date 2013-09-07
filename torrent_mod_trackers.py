#!/usr/bin/env python

# Copyright (C) 2013  Marco Chieppa (aka crap0101)

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
from collections import MutableSequence
import os
import re
import sys

# external import
import bencode

_VERSION = '0.1'

ANNOUNCE = 'announce'
ANNOUNCE_LIST = 'announce-list'
ENC = 'utf-8'

def flatlist (seq):
    res = []
    for s in seq:
        if isinstance(s, MutableSequence):
            res.extend(flatlist(s))
        else:
            res.append(s)
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

def remove_trackers (path, trackers, use_regex=False, backup_suffix='.bk'):
    with open(path, 'rb') as file:
        data = file.read()
    meta = bencode.bdecode(data)
    if use_regex:
        def match (tracker, test):
            return re.match(test, tracker)
    else:
        def match (tracker, test):
            return tracker == test
    for t in trackers:
        if match(t, meta[ANNOUNCE]):
            meta[ANNOUNCE] = b''
            break
    alist = meta.get(ANNOUNCE_LIST, [])
    if alist:
        for lst in alist:
            rem = []
            for tp in lst:
                for tr in trackers:
                    if match(tp, tr):
                        rem.append(tp)
            if rem:
                for r in rem:
                    lst.remove(r)
                rem = []
        filtered_list = list(filter(None, alist))
        if not filtered_list:
            meta.pop(ANNOUNCE_LIST)
        else:
            meta[ANNOUNCE_LIST] = filtered_list
    if backup_suffix:
        os.rename(path, path+backup_suffix)
    with open(path, 'wb') as file:
        file.write(bencode.bencode(meta))


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description="add or remove trackers from a torrent file")
    p.add_argument('file', help='torrent file')
    p.add_argument('trackers', nargs='*', help='trakers to add')
    p.add_argument('-b', '--backup', dest='backup', nargs='?', const='.bk',
                   default='', metavar='SUFFIX', help='make a backup of the '
                   'original file, renamed adding SUFFIX. Default: %(const)s')
    p.add_argument('-f', '--from-file', dest='from_file', metavar='PATH',
                   help='read trackers for PATH (one per line). '
                        'Empty lines or lines starting with "#" are ignored.')
    p.add_argument('-r', '--remove', dest='remove', action='store_true',
                   help='remove listed trackers instead of add them')
    p.add_argument('-R', '--regex', dest='use_regex', action='store_true',
                   help='when removing, interpret trackers strings as regex'
                   ' patterns. Every trackers matching them will be removed')
    p.add_argument('-v', '--version', action='version', version=_VERSION)
    args = p.parse_args()
    if args.from_file:
        with open(args.from_file) as tfile:
            from_file = []
            for tr in tfile:
                tr = tr.strip()
                if tr and not tr.startswith('#'):
                    from_file.append(tr)
            args.trackers.extend(from_file)
    if not args.trackers:
        p.error("No trackers to add!")
    trackers = [t.encode(ENC) for t in args.trackers]
    if args.remove:
        remove_trackers (args.file, trackers, args.use_regex, args.backup)        
    else:
        add_trackers(args.file, trackers, args.backup)
