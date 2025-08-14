#!/usr/bin/env python3

# Copyright (C) 2013-2025  Marco Chieppa (aka crap0101)

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
from collections.abc import MutableSequence
import os
import re
import sys

# external import
try:
    import bencode
except ImportError:
    import fastbencode as bencode

_VERSION = '0.2'

ANNOUNCE = b'announce'
ANNOUNCE_LIST = b'announce-list'
ENC = 'utf-8'
BK = '.bk'

def flatlist (seq):
    res = []
    for s in seq:
        if isinstance(s, MutableSequence):
            res.extend(flatlist(s))
        else:
            res.append(s)
    return res

def get_data (file):
    with open(file, 'rb') as f:
        return bencode.bdecode(f.read())

def add_trackers (path, trackers, announce_tracker, backup_suffix):
    meta = get_data(path)
    if announce_tracker != None:
            meta[ANNOUNCE] = announce_tracker
    alist = meta.get(ANNOUNCE_LIST, [meta[ANNOUNCE]])
    trackerlist = flatlist(alist)
    alist.extend([t] for t in set(trackers).difference(trackerlist))
    meta[ANNOUNCE_LIST] = alist
    if backup_suffix:
        os.rename(path, path+backup_suffix)
    with open(path, 'wb') as file:
        file.write(bencode.bencode(meta))

def remove_trackers (path, trackers, backup_suffix, use_regex=False):
    meta = get_data(path)
    if use_regex:
        def match (tracker, test):
            return re.match(test, tracker)
    else:
        def match (tracker, test):
            return tracker == test
    for t in trackers:
        if match(meta[ANNOUNCE], t):
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
        meta[ANNOUNCE_LIST] = list(filter(None, alist))
    if backup_suffix:
        os.rename(path, path+backup_suffix)
    with open(path, 'wb') as file:
        file.write(bencode.bencode(meta))


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description="add or remove trackers from a torrent file")
    p.add_argument('files', nargs='+', help='torrent files')
    p.add_argument('-A', '--announce',
                   dest='announce_tracker', default=None,
                   help='add this tracker (or replace an existing one)'
                   ' as the announce traker.')
    p.add_argument('-t', '--trackers',
                   nargs='*', dest='trackers', default=[],
                   help='trakers to add/remove')
    p.add_argument('-b', '--backup', dest='backup', nargs='?', const=BK,
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
    backup = bytes(args.backup, ENC)
    trackers = list(bytes(t, ENC) for t in args.trackers)
    if args.announce_tracker != None:
        if args.remove:
            p.error('-A and -r used together!')
        atracker = bytes(args.announce_tracker, ENC)
    else:
        atracker = args.announce_tracker
    if args.from_file:
        with open(args.from_file) as tfile:
            from_file = []
            for tr in tfile:
                tr = tr.strip()
                if tr and not tr.startswith('#'):
                    from_file.append(bytes(tr, ENC))
            trackers.extend(from_file)
    if not trackers:
        p.error("No trackers specified!")
    if args.remove:
        for file in args.files:
            remove_trackers (file, trackers, backup, args.use_regex)        
    else:
        for file in args.files:
            add_trackers(file, trackers, atracker, backup)
